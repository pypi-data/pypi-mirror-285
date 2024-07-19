from __future__ import annotations

import asyncio
import inspect
import traceback

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, Generic, TypeVar, overload

from .misc import ClassProperty, is_loop_running

if TYPE_CHECKING:
	try:
		from typing import Self

	except ImportError:
		from typing_extensions import Self


T = TypeVar("T")
SignalCallback = Callable[..., Awaitable[bool | None]]
MainSignalCallback = Callable[..., Awaitable[None]]


class Property(Generic[T]):
	"Descriptor to manage an attribute of an :class:`Object`"

	key: str
	"Name of the attribute"


	def __init__(self, default: T | None = None) -> None:
		"""
			Create a new ``Property`` object

			:param default: Default value to return. A :class:`KeyError` will instead be raised if
				no default is set.
		"""

		self.default: T | None = default
		"Default value to return if one is not set"


	def __repr__(self) -> str:
		if not hasattr(self, "key"):
			return f"Property(default = {repr(self.default)})"

		return f"Property({repr(self.key)}, default = {repr(self.default)})"


	def __set_name__(self, obj: Object, name: str) -> None:
		self.key = name

		if not hasattr(obj, "_props"):
			obj._props = {}

		if not hasattr(obj, "_values"):
			obj._values = {}

		obj._props[name] = self


	@overload
	def __get__(self, obj: Object, cls: Any) -> T:
		...


	@overload
	def __get__(self, obj: None, cls: Any) -> Self:
		...


	def __get__(self, obj: Object | None, cls: Any) -> T | Self:
		if obj is None:
			return self

		if (value := obj._values.get(self.key, self.default)) is None:
			raise KeyError(self.key)

		return value # type: ignore[no-any-return]


	def __set__(self, obj: Object, value: T) -> None:
		obj._values[self.key] = value
		obj.notify.emit(self.key, value)


	def __delete__(self, obj: Object) -> None:
		obj._values[self.key] = self.default
		obj.notify.emit(self.key, self.default)


class SignalObj:
	"Represents a signal for a specific object"


	def __init__(self,
				obj: Any,
				key: str,
				callback: MainSignalCallback | None,
				timeout: float | int) -> None:

		self.object: Any = obj
		"The object this signal is attached to"

		self.key: str = key
		"Name of the signal attribute"

		self.timeout: float | int = timeout
		"How long to wait before canceling the callback. Set to ``0.0`` or less to disable this."

		self.callback: MainSignalCallback | None = callback
		"Function to call after all of the other callbacks when the signal is emitted"

		self.callbacks: list[SignalCallback] = []
		"Functions to call when the signal is emitted"


	def emit(self, *args: Any, **kwargs: Any) -> None:
		"""
			Call all of the callbacks in the order they were added as well as the associated
			function.

			If any callback returns `True`, all other callbacks get skipped.

			:param args: Positional arguments to pass to all of the callbacks
			:param kwargs: Keyword arguments to pass to all of the callbacks
		"""

		if not is_loop_running():
			raise RuntimeError("Event loop is not running")

		asyncio.create_task(self.handle_emit(*args, **kwargs))


	def connect(self, callback: SignalCallback) -> SignalCallback:
		"""
			Add a function to the list of callbacks. Can be used as a decorator.

			:param callback: A callable or coroutine
		"""

		if not inspect.iscoroutinefunction(callback):
			raise TypeError(f"Not a coroutine: {callback.__name__}")

		if callback not in self.callbacks:
			self.callbacks.append(callback)

		return callback


	def disconnect(self, callback: SignalCallback) -> None:
		"""
			Remove a function from the list of callbacks

			:param callback: A callable or coroutine
		"""

		if not self.callback:
			# oh boy something really goofed
			return

		try:
			self.callbacks.remove(callback)

		except ValueError:
			cbname = callback.__name__
			signame = self.callback.__name__
			print(f"WARNING: '{cbname}' was not connted to signal '{signame}'")


	async def handle_emit(self, *args: Any, catch_errors: bool = True, **kwargs: Any) -> None:
		"""
			This gets called by :meth:`Signal.emit` as an :class:`asyncio.Task`.

			:param args: Positional arguments to pass to all of the callbacks
			:param kwargs: Keyword arguments to pass to all of the callbacks
			:param catch_errors: Whether or not to handle exceptions raised from callbacks
		"""

		for callback in self.callbacks:
			try:
				if await self.handle_callback(callback, *args, **kwargs):
					break

			except Exception:
				if not catch_errors:
					raise

				traceback.print_exc()
				break

		if self.callback is None:
			return

		try:
			await self.handle_callback(self.callback, *args, **kwargs)

		except Exception:
			if not catch_errors:
				raise

			traceback.print_exc()


	async def handle_callback(self,
							callback: SignalCallback,
							*args: Any,
							**kwargs: Any) -> bool | None:

		arguments = list(args)

		if getattr(callback, "__self__", None) != self.object:
			arguments.insert(0, self.object)

		if self.timeout <= 0.0:
			return await callback(*arguments, **kwargs)

		try:
			# asyncio.timeout and asyncio.wait_for complain, so need to find a new way
			# update: it doesn't complain anymore? keeping this comment here just in case
			async with asyncio.timeout(self.timeout):
				return await callback(*arguments, **kwargs)

		except TimeoutError:
			print(f"Callback '{callback.__name__}' timed out")
			return True


class Signal:
	"Allows a series of callbacks to get called via async. Use as a decorator for the base function."

	key: str
	cls: type


	def __init__(self, timeout: float | int = 0.0):
		"""
			:param timeout: Time in seconds to wait before cancelling the callback
		"""

		self.timeout: float | int = timeout
		self.callback: MainSignalCallback | None = None


	def __call__(self, callback: MainSignalCallback) -> Self:
		if not inspect.iscoroutinefunction(callback):
			raise TypeError(f"Not a coroutine: {callback.__name__}")

		self.callback = callback

		self.__doc__ = callback.__doc__
		self.__annotations__ = callback.__annotations__

		return self


	def __set_name__(self, cls: type[Object], name: str) -> None:
		self.cls = cls
		self.key = name


	@overload
	def __get__(self, obj: Object, cls: Any) -> SignalObj:
		...


	@overload
	def __get__(self, obj: None, cls: Any) -> Self:
		...


	def __get__(self, obj: Object | None, cls: Any) -> SignalObj | Self:
		if obj is None:
			return self

		if not hasattr(obj, "_signals"):
			obj._signals = {}

		if self.key not in obj._signals:
			obj._signals[self.key] = SignalObj(obj, self.key, self.callback, self.timeout)

		return obj._signals[self.key]


class ObjectMeta(type):
	def __new__(cls, name: str, subclasses: tuple[type], data: dict[str, Any]) -> type:
		for key, annotation in data.get("__annotations__", {}).items():
			if key.startswith("_"):
				continue

			if key not in data:
				data[key] = Property()

			elif not isinstance(data[key], Property):
				data[key] = Property(data[key])

		return type.__new__(cls, name, subclasses, data)


class Object(metaclass = ObjectMeta):
	"Enhanced :class:`object`"

	_props: dict[str, Property[Any]]
	_values: dict[str, Any]
	_signals: dict[str, SignalObj]


	@ClassProperty
	def properties(cls: type[Self]) -> tuple[Property[Any], ...]: # type: ignore[misc]
		return tuple(cls._props.values())


	@Signal(5.0)
	async def notify(self, key: str, value: Any) -> None:
		"""
			:class:`blib.Signal` that gets emitted when a property has been set

			:param key: Name of the property
			:param value: New property that has been set
		"""
