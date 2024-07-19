from __future__ import annotations

import asyncio
import contextlib
import json
import os
import random
import statistics
import string
import timeit
import traceback

from collections.abc import Callable, Generator, Iterator, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
from http.client import HTTPResponse
from importlib.resources import files as pkgfiles
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generic, TypeVar, overload
from urllib.request import Request, urlopen

from . import __version__
from .enums import FileSizeUnit, HttpMethod

if TYPE_CHECKING:
	try:
		from typing import Self

	except ImportError:
		from typing_extensions import Self


T = TypeVar("T")
C = TypeVar("C", bound = type)
DictValueType = TypeVar("DictValueType")
SPType = TypeVar("SPType")

TRUE_STR = ['on', 'y', 'yes', 'true', 'enable', 'enabled', '1']
FALSE_STR = ['off', 'n', 'no', 'false', 'disable', 'disable', '0']

TLD_CACHE_URL = "https://publicsuffix.org/list/public_suffix_list.dat"
TLD_CACHE_PATH = Path("~/.cache").expanduser().joinpath('public_suffix_list.txt')
TLD_CACHE_DATA: list[str] = []


@contextlib.contextmanager
def catch_errors(suppress: bool = False) -> Generator[None, None, None]:
	"""
		Context manager for running a block of code and catching any errors that get raised

		:param suppress: If ``True``, don't print a raised exception
	"""
	try:
		yield

	except Exception:
		if not suppress:
			traceback.print_exc()


def convert_to_boolean(value: Any) -> bool:
	"""
		Convert an object to :class:`bool`. If it can't be directly converted, ``True``
		is returned.

		:param value: Object to be converted
	"""
	if value is None:
		return False

	if isinstance(value, bool):
		return value

	if isinstance(value, str):
		if value.lower() in TRUE_STR:
			return True

		if value.lower() in FALSE_STR:
			return False

	if isinstance(value, int):
		if value == 1:
			return True

		if value == 0:
			return False

	return bool(value)


def convert_to_bytes(value: Any, encoding: str = "utf-8") -> bytes:
	"""
		Convert an object to :class:`bytes`

		:param value: Object to be converted
		:param encoding: Character encoding to use if the object is a string or gets converted to
			one in the process
		:raises TypeError: If the object cannot be converted
	"""
	if isinstance(value, bytes):
		return value

	try:
		return convert_to_string(value).encode(encoding)

	except TypeError:
		raise TypeError(f"Cannot convert '{get_object_name(value)}' into bytes") from None


def convert_to_string(value: Any, encoding: str = 'utf-8') -> str:
	"""
		Convert an object to :class:`str`

		:param value: Object to be converted
		:param encoding: Character encoding to use if the object is a :class:`bytes` object
	"""
	if isinstance(value, bytes):
		return value.decode(encoding)

	if isinstance(value, bool):
		return str(value)

	if isinstance(value, str):
		return value

	if isinstance(value, (dict, list, tuple, set)):
		return json.dumps(value)

	if isinstance(value, (int, float)):
		return str(value)

	if value is None:
		return ''

	raise TypeError(f'Cannot convert "{get_object_name(value)}" into a string') from None


def deprecated(new_method: str, version: str, remove: str | None = None) -> Callable[..., Any]:
	"""
		Decorator to mark a function as deprecated and display a warning on first use.

		:param new_method: Name of the function to replace the wrapped function
		:param version: Version of the module in which the wrapped function was considered
			deprecated
		:param remove: Version the wrapped function will get removed
	"""

	called = False

	def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
		@wraps(func)
		def inner(*args: Any, **kwargs: Any) -> Any:
			if not called:
				name = func.__qualname__ if hasattr(func, "__qualname__") else func.__name__

				if not remove:
					print(f"WARN: {name} was deprecated in {version}. Use {new_method} instead.")

				else:
					msg = f"WARN: {name} was deprecated in {version} and will be removed in "
					msg += f"{remove}. Use {new_method} instead."
					print(msg)

			return func(*args, **kwargs)
		return inner
	return wrapper


def get_object_name(obj: Any) -> str:
	"""
		Get the name of an object

		:param obj: Object to get the name of
	"""

	try:
		return obj.__name__ # type: ignore[no-any-return]

	except AttributeError:
		return type(obj).__name__


def get_object_properties(
						obj: Any,
						ignore_descriptors: bool = True,
						ignore_underscore: bool = True) -> Iterator[tuple[str, Any]]:
	"""
		Get an objet's properties and their values

		:param obj: Object to get the properties of
		:param ignore_descriptors: Don't get the value of descriptor objects (ex. ``@property``)
		:param ignore_underscore: Skip properties that start with an underscore (``_``)
	"""

	for key in dir(obj):
		if ignore_descriptors and key in dir(type(obj)):
			continue

		if ignore_underscore and key.startswith("_"):
			continue

		if callable(value := getattr(obj, key)):
			continue

		yield key, value


def get_resource_path(module: str, path: str | None = None) -> Path:
	"""
		Get a path to a module resource

		:param module: Name of the module to get the resource from
		:param path: Path of the resource starting from the path of the module
	"""

	new_path = Path(str(pkgfiles(module)))
	return new_path.joinpath(path.lstrip("/")) if path is not None else new_path


def get_top_domain(domain: str) -> str:
	'''
		Get the main domain from a string. The top-level domain list is cached as
		``~/.cache/public_suffix_list.txt`` for 7 days

		:param str domain: The domain to extract the top-level domain from
		:raises ValueError: When the top domain cannot be found
	'''

	global TLD_CACHE_DATA

	if len(TLD_CACHE_DATA) == 0:
		exists = TLD_CACHE_PATH.exists()

		try:
			modified = datetime.fromtimestamp(TLD_CACHE_PATH.stat().st_mtime)

		except FileNotFoundError:
			modified = None

		if not exists or not modified or modified + timedelta(days=7) < datetime.now():
			TLD_CACHE_PATH.parent.mkdir(exist_ok = True, parents = True)

			with TLD_CACHE_PATH.open("wt", encoding = "utf-8") as fd:
				with http_request(TLD_CACHE_URL) as resp:
					for line in resp.read().decode('utf-8').splitlines():
						if 'end icann domains' in line.lower():
							break

						if not line or line.startswith('//'):
							continue

						if line.startswith('*'):
							line = line[2:]

						fd.write(line + "\n")

		with TLD_CACHE_PATH.open("r", encoding = "utf-8") as fd:
			TLD_CACHE_DATA = list(fd.read().splitlines())

	domain_split = domain.split('.')

	try:
		if '.'.join(domain_split[-2:]) in TLD_CACHE_DATA:
			return '.'.join(domain_split[-3:])

	except IndexError:
		pass

	if '.'.join(domain_split[-1:]) in TLD_CACHE_DATA:
		return '.'.join(domain_split[-2:])

	raise ValueError('Cannot find TLD')


def http_request(
				url: str,
				data: Any = None,
				headers: dict[str, str] | None = None,
				method: HttpMethod | str = HttpMethod.GET,
				timeout: int = 60) -> HTTPResponse:
	"""
		Make an http request. The default User-Agent is "blib/:attr:`BLib.__version__`"

		:param url: Url to send the request to
		:param data: Data to send with the request. Must be parsable by :class:`convert_to_bytes`.
		:param method: HTTP method to use when making the request
		:param headers: HTTP header key/value pairs to send with the request
		:param timeout: How long to wait when connecting before giving up

		:raises TimeoutError: When the connection was not established before the timeout limit
		:raises urllib.error.HTTPError: When the server returns an error
	"""

	method = HttpMethod.parse(method)

	if not headers:
		headers = {}

	else:
		headers = {key.title(): value for key, value in headers.items()}

	if headers.get("User-Agent") is None:
		headers["User-Agent"] = f"BLib/{__version__}"

	request = Request(
		url = url,
		method = method.upper(),
		data = convert_to_bytes(data) if data else None,
		headers = headers
	)

	return urlopen(request, timeout = timeout) # type: ignore[no-any-return]


def is_loop_running() -> bool:
	"Check if an event loop is running in the current thread"

	try:
		return asyncio.get_running_loop().is_running()

	except RuntimeError:
		return False


def random_str(
			length: int = 20,
			letters: bool = True,
			numbers: bool = True,
			capital: bool = False,
			extra: str = "") -> str:
	"""
		Return a randomly generated string. Uses alphanumeric characters by default, but more can
		be specified as a string.

		:param length: Length of the resulting string in characters
		:param letters: Include all ascii letters
		:param numbers: Include numbers
		:param capital: Include uppercase ascii letters if ``letters`` is ``True``
		:param extra: Characters to also include in the resulting string
	"""

	characters = extra

	if letters:
		characters += string.ascii_letters

		if capital:
			characters += string.ascii_letters.upper()

	if numbers:
		characters += string.digits

	return "".join(random.choices(characters, k = length))


def time_function(
				func: Callable[..., Any],
				*args: Any,
				passes: int = 1,
				use_gc: bool = True,
				**kwargs: Any) -> RunData:
	"""
		Call a function n times and return each run time, the average time, and the total time in
		miliseconds

		:param func: Function to call
		:param args: Positional arguments to pass to the function
		:param passes: Number of times to call the function
		:param use_gc: Enable garbage collection during the runs
		:param kwargs: Keyword arguments to pass to the function
	"""

	if use_gc:
		timer = timeit.Timer(lambda: func(*args, **kwargs), "gc.enable()")

	else:
		timer = timeit.Timer(lambda: func(*args, **kwargs))

	if passes > 1:
		times = timer.repeat(passes, 1)

	else:
		times = [timer.timeit(1)]

	return RunData(tuple(times), statistics.fmean(times), sum(times))


def time_function_pprint(
					func: Callable[..., Any],
					*args: Any,
					passes: int = 5,
					use_gc: bool = True,
					floatout: bool = True,
					**kwargs: Any) -> RunData:
	"""
		Prints out readable results from ``time_function`` and returns the raw data. Convert the
		printed times to an ``int`` by setting ``floatout`` to ``False``

		:param func: Function to call
		:param args: Positional arguments to pass to the function
		:param passes: Number of times to call the function
		:param use_gc: Enable garbage collection during the runs
		:param floatout: Print values as ``float`` instead of ``int``
		:param kwargs: Keyword arguments to pass to the function
	"""

	data = time_function(func, *args, **kwargs, passes = passes, use_gc = use_gc)

	for idx, passtime in enumerate(data.runs):
		if not floatout:
			print(f"Pass {idx+1}: {passtime:.0f}")

		else:
			print(f"Pass {idx+1}: {passtime:.8f}")

	print("-----------------")

	if not floatout:
		print(f"Average: {data.average:.0f}")
		print(f"Total: {data.total:.0f}")

	else:
		print(f"Average: {data.average:.8f}")
		print(f"Total: {data.total:.8f}")

	return data


# mypy complains when `type[Self]` is used for decorated methods
class ClassProperty(Generic[T]):
	def __init__(self, func: Callable[[C], T]) -> None:
		self.func: Callable[[C], T]


	@overload
	def __get__(self, obj: Any, cls: C) -> T:
		...


	@overload
	def __get__(self, obj: Any, cls: None) -> Self:
		...


	def __get__(self, obj: Any, cls: C | None) -> T | Self:
		if cls is None:
			return self

		return self.func(cls)


class DictProperty(Generic[DictValueType]):
	"Represents a key in a dict"


	def __init__(self,
				key: str,
				deserializer: Callable[[str, Any], DictValueType] | None = None,
				serializer: Callable[[str, DictValueType], Any] | None = None) -> None:
		"""
			Create a new dict property

			:param key: Name of the key to be handled by this ``Property``
			:param deserializer: Function that will convert a JSON value to a Python value
			:param serializer: Function that will convert a Python value to a JSON value
		"""

		self.key: str = key
		self.deserializer: Callable[[str, Any], Any] | None = deserializer
		self.serializer: Callable[[str, Any], Any] | None = serializer


	def __get__(self,
				obj: dict[str, DictValueType | Any] | None,
				objtype: Any = None) -> DictValueType:

		if obj is None:
			raise RuntimeError("No object for dict property")

		try:
			value = obj[self.key]

		except KeyError:
			objname = get_object_name(obj)
			raise AttributeError(f"'{objname}' has no attribute '{self.key}'") from None

		if self.deserializer is None:
			return value

		return self.deserializer(self.key, value) # type: ignore[no-any-return]


	def __set__(self, obj: dict[str, DictValueType | Any], value: DictValueType) -> None:
		if self.serializer is None:
			obj[self.key] = value
			return

		obj[self.key] = self.serializer(self.key, value)


	def __delete__(self, obj: dict[str, DictValueType | Any]) -> None:
		del obj[self.key]


class Env:
	"Easy access to environmental variables"


	@staticmethod
	def get(key: str,
			default: Any = None,
			converter: Callable[[str], Any] = str) -> Any:
		"""
			Get an environmental variable

			:param key: Name of the variable
			:param converter: Function to convert the value to a different type
			:param default: The default value to return if the key is not found
		"""

		try:
			return converter(os.environ[key])

		except KeyError:
			return default


	@classmethod
	def get_array(cls: type[Env],
				key: str,
				separator: str = ":",
				converter: Callable[[str], Any] = str) -> Iterator[Any]:
		"""
			Get an environmental variable as an iterator of items

			:param key: Name of the variable
			:param separator: String to use to split items
			:param converter: Function to convert each value to a different type
		"""

		for value in cls.get(key, "").split(separator):
			yield (converter(value.strip()))


	@classmethod
	def get_int(cls: type[Env], key: str, default: int = 0) -> int:
		"""
			Get an environmental variable as an ``int``

			:param key: Name of the variable
			:param default: The default value to return if the key is not found
		"""

		return cls.get(key, default, int) # type: ignore[no-any-return]


	@classmethod
	def get_float(cls: type[Env], key: str, default: float = 0.0) -> float:
		"""
			Get an environmental variable as a ``float``

			:param key: Name of the variable
			:param default: The default value to return if the key is not found
		"""

		return cls.get(key, default, float) # type: ignore[no-any-return]


	@classmethod
	def get_bool(cls: type[Env], key: str, default: bool = False) -> bool:
		"""
			Get an environmental variable as a ``bool``

			:param key: Name of the variable
			:param default: The default value to return if the key is not found
		"""

		return cls.get(key, default, convert_to_boolean) # type: ignore[no-any-return]


	@classmethod
	def get_json(cls: type[Env], key: str, default: dict[Any, Any] | None = None) -> JsonBase:
		"""
			Get an environmental variable as a JSON-parsed ``dict``

			:param key: Name of the variable
			:param default: The default value to return if the key is not found
		"""

		return cls.get(key, default, JsonBase.parse) # type: ignore[no-any-return]


	@classmethod
	def get_list(cls: type[Env],
				key: str,
				separator: str = ":",
				converter: Callable[[str], Any] = str) -> list[Any]:
		"""
			Get an environmental variable as a ``tuple``

			:param key: Name of the variable
			:param separator: String to use to split items
			:param converter: Function to convert each value to a different type
		"""

		return list(cls.get_array(key, separator, converter))


	@classmethod
	def get_tuple(cls: type[Env],
				key: str,
				separator: str = ":",
				converter: Callable[[str], Any] = str) -> tuple[Any]:
		"""
			Get an environmental variable as a ``tuple``

			:param key: Name of the
			:param separator: String to use to split items
			:param converter: Function to convert each value to a different type
		"""

		return tuple(cls.get_list(key, separator, converter))


	@classmethod
	def get_set(cls: type[Env],
				key: str,
				separator: str = ":",
				converter: Callable[[str], Any] = str) -> set[Any]:
		"""
			Get an environmental variable as a ``set``

			:param key: Name of the variable
			:param separator: String to use to split items
			:param converter: Function to convert each value to a different type
		"""

		return set(cls.get_list(key, separator, converter))


	@classmethod
	def keys(cls: type[Env]) -> Iterator[str]:
		"Fetch all environmental variable names"

		for key in os.environ:
			yield key


	@classmethod
	def items(cls: type[Env]) -> Iterator[tuple[str, str]]:
		"Fetch all environmental variable names and values"

		for key in os.environ:
			yield key, os.environ[key]


	@classmethod
	def values(cls: type[Env]) -> Iterator[str]:
		"Fetch all environmental variable values"

		for value in os.environ.values():
			yield value


class FileSize(int):
	"Converts a human-readable file size to bytes"


	def __new__(cls: type[Self],
				size: int | float,
				unit: FileSizeUnit | str = FileSizeUnit.B) -> Self:

		return int.__new__(cls, FileSizeUnit.parse(unit).multiply(size))


	def __repr__(self) -> str:
		value = int(self)
		return f"FileSize({value:,} bytes)"


	def __str__(self) -> str:
		return int.__str__(self)


	@classmethod
	def parse(cls: type[Self], text: str) -> Self:
		"""
			Parse a file size string

			:param text: String representation of a file size
			:raises AttributeError: If the text cannot be parsed
		"""

		size_str, unit = text.strip().split(" ", 1)
		size = float(size_str)
		unit = FileSizeUnit.parse(unit)

		return cls(size, unit)


	def to_optimal_string(self) -> str:
		"""
			Attempts to display the size as the highest whole unit
		"""
		index = 0
		size: int | float = int(self)

		while True:
			if size < 1024 or index == 8:
				unit = FileSizeUnit.from_index(index)
				return f'{size:.2f} {unit}'

			try:
				index += 1
				size = self / FileSizeUnit.from_index(index).multiplier

			except IndexError:
				raise ValueError('File size is too large to convert to a string') from None


	def to_string(self, unit: FileSizeUnit, decimals: int = 2) -> str:
		"""
			Convert to the specified file size unit

			:param unit: Unit to convert to
			:param decimals: Number of decimal points to round to
		"""
		unit = FileSizeUnit.parse(unit)

		if unit == FileSizeUnit.BYTE:
			return f'{self} B'

		size = round(self / unit.multiplier, decimals)
		return f'{size} {unit}'


class JsonBase(dict[str, Any]):
	"A ``dict`` with methods to convert to JSON and back"


	@classmethod
	def parse(cls: type[Self], data: str | bytes | Mapping[str, Any]) -> Self:
		"""
			Parse a JSON object

			:param data: JSON object to parse
			:raises TypeError: When an invalid object type is provided
		"""

		if isinstance(data, (str, bytes)):
			data = json.loads(data)

		if isinstance(data, cls):
			return data

		if not isinstance(data, dict):
			raise TypeError(f"Cannot parse objects of type \"{type(data).__name__}\"")

		return cls(data)


	def to_json(self, indent: int | str | None = None, **kwargs: Any) -> str:
		"""
			Return the message as a JSON string

			:param indent: Number of spaces or the string to use for indention
			:param kwargs: Keyword arguments to pass to :func:`json.dumps`
		"""

		return json.dumps(self, indent = indent, default = self.handle_value_dump, **kwargs)


	def handle_value_dump(self, value: Any) -> Any:
		"""
			Gets called when a value is of the wrong type and needs to be converted for dumping to
			json. If the type is unknown, it will be forcibly converted to a ``str``.

			:param value: Value to be converted
		"""

		if not isinstance(value, (str, int, float, bool, dict, list, tuple, type(None))):
			# print(f"Warning: Cannot properly convert value of type '{type(value).__name__}'")
			return str(value)

		return value


class NamedTuple(tuple[tuple[str, Any], ...]):
	"A tuple with dict-like access of items"

	slots = ("_keys", )
	_keys: tuple[str, ...]


	def __new__(cls: type[Self],
				keys: Sequence[str],
				values: Sequence[Any]) -> Self:
		"""
			Create a new ``NamedTuple`` object. ``kwargs`` will override any matching keys in
			``_items``.

			:param _items: ``dict`` object of key/value pairs to add
			:param kwargs: key/value pairs to add
		"""

		if len(keys) != len(values):
			raise ValueError("Keys and values must be the same length")

		data = tuple.__new__(cls, zip(keys, values))
		data._keys = tuple(keys)
		return data


	def __getitem__(self, key: int | str) -> Any: # type: ignore[override]
		if isinstance(key, str):
			key = self._keys.index(key)

		return tuple.__getitem__(self, key)[1]


	def __repr__(self) -> str:
		data = ", ".join(f"{key}={repr(value)}" for key, value in self.items())
		return f"NamedTuple({data})"


	@classmethod
	def from_dict(cls: type[Self], data: dict[str, Any]) -> Self:
		return cls(tuple(data.keys()), tuple(data.values()))


	def keys(self) -> Iterator[str]:
		"Keys associated with each value"

		for key in self._keys:
			yield key


	def items(self) -> Iterator[tuple[str, Any]]:
		"Key/value pairs as a tuple of tuples"

		for item in self:
			yield item


	def to_dict(self) -> dict[str, Any]:
		"Convert to a :class:`dict`"

		return dict(self)


	def values(self) -> Iterator[Any]:
		"Iterate throug the values"

		for key, value in self:
			yield value


@dataclass
class RunData:
	"Data returned from :meth:`time_function` and `time_function_pprint`"

	runs: tuple[float, ...]
	"Elapsed time of each run"

	average: float
	"Average time of all runs"

	total: float
	"Time it took for all runs"


class StaticProperty(Generic[SPType]):
	"Decorator for turning a static method into a static property"

	def __init__(self, func: Callable[..., SPType]) -> None:
		"""
			Create a new ``StaticProperty`` object

			:param func: The decorated function
		"""

		self._getter: Callable[[], SPType] = func
		self._setter: Callable[[Any], None] | None = None


	def __get__(self, obj: Any, cls: Any) -> SPType:
		return self._getter()


	def __set__(self, obj: Any, value: Any) -> None:
		if self._setter is None:
			raise AttributeError("No setter is set")

		self._setter(value)


	def setter(self, func: Callable[[Any], None]) -> Callable[[Any], None]:
		"""
			Add a function for setting the value

			:param func: Function to decorate
		"""

		self._setter = func
		return func
