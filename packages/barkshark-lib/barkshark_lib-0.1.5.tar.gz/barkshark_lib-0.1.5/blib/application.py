from __future__ import annotations

import asyncio
import signal

from typing import Any

from .objects import Object, Signal


APPS: dict[str, Application] = {}


class Application(Object):
	"Easy to use class for managing an event loop"


	def __init__(self, name: str):
		"""
			Create a new ``Application`` object

			:param name: Identifier for the application
		"""

		self.name: str = name
		"Identifier for the application"

		self.exit_code: int | None = None
		"Status code set when the application quits"

		self.loop: asyncio.AbstractEventLoop | None = None
		"Event loop associated with the application if it is running"

		self.signals: list[int] = [
			signal.SIGHUP,
			signal.SIGILL,
			signal.SIGTERM,
			signal.SIGINT
		]
		"List of signals to handle while the loop is running"

		self._shutdown = asyncio.Event()
		Application.set(self)


	@staticmethod
	def get(name: str, create: bool = True) -> Application:
		"""
			Get the default application if one is set

			:param name: Identifier of the application to fetch
			:param create: Create a new application if it does not exist
			:raises KeyError: If ``create`` is ``False`` and the application does not exist
		"""

		try:
			return APPS[name]

		except KeyError:
			if create:
				return Application(name)

			raise


	@staticmethod
	def set(app: Application) -> None:
		"""
			Set an application as the default

			.. note:: A new application will set itself as the default on init if one is not already
				set

			:param app: The application to be set as default
			:raises KeyError: If an application of the same name exists
		"""

		if app.name in APPS:
			raise KeyError(app.name)

		APPS[app.name] = app


	@Signal(5.0)
	async def shutdown(self) -> None:
		"""
			:class:`Signal` that gets called before the loop closes

			:param Application app: Application that emit the signal
			:returns: Return ``True`` to prevent all other handlers from being called
		"""

		if self.loop is None:
			raise RuntimeError("No async loop is active")

		for sig in self.signals:
			try:
				self.loop.add_signal_handler(sig, signal.SIG_DFL) # type: ignore[arg-type]

			except ValueError:
				print(f"Cannot handle signal: {sig}")

		self.loop = None


	@Signal(5.0)
	async def startup(self) -> None:
		"""
			:class:`Signal` that gets called after the loop starts

			:param Application app: Application that emit the signal
			:returns: Return ``True`` to prevent all other handlers from being called
		"""

		if self.loop is None:
			raise RuntimeError("No async loop is active")

		for sig in self.signals:
			try:
				self.loop.add_signal_handler(sig, self.__quit)

			except ValueError:
				print(f"Cannot handle signal: {sig}")


	@property
	def running(self) -> bool:
		"Whether or not the application is currently running"

		return self.loop is not None and self.loop.is_running()


	def kill(self) -> None:
		"Imediately stop the loop"

		if self.loop is None:
			return

		self.loop.stop()
		self.loop = None

		self._shutdown.clear()


	def quit(self, exit_code: int = 0) -> None:
		"Tell the application to quit"

		self._shutdown.set()
		self.exit_code = exit_code


	def run(self) -> int | None:
		"""
			Starts the application and sets a return code on exit

			:returns: A return code
		"""

		if self.running:
			return self.exit_code

		self.exit_code = None
		self._shutdown.clear()

		asyncio.run(self.handle_run())
		self.loop = None

		if self.exit_code is None:
			self.exit_code = 0

		return self.exit_code


	def __quit(self, *_: Any) -> None:
		self.quit()


	async def handle_run(self) -> None:
		"Function that starts up the application and handles the event loop"

		self.loop = asyncio.get_running_loop()
		self.startup.emit()

		while not self._shutdown.is_set():
			await self.handle_loop()

		self.shutdown.emit()


	async def handle_loop(self) -> None:
		"""
			Function that gets ran while the loop is running. It is recommended to add a
			:func:`asyncio.sleep` call at the end.
		"""
		await asyncio.sleep(0.1)
