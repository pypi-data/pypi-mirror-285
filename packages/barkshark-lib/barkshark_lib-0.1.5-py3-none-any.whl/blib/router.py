from __future__ import annotations

# All of this will eventually get moved to barkshark-asgi

import re

from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING, Any

from .enums import HttpMethod
from .errors import HttpError
from .misc import convert_to_boolean, get_object_name
from .path import File, Path

if TYPE_CHECKING:
	try:
		from typing import Self

	except ImportError:
		from typing_extensions import Self


RouteHandler = Callable[..., Any]
TypeConverter = Callable[[str], Any]

ROUTERS: list[Router] = []


def parse_path(path: str, trailing_slash: bool) -> str:
	"Make sure a path starts and (optionally) ends with ``/``"

	if not path.startswith('/'):
		path = '/' + path

	if not path.endswith('/') and trailing_slash:
		path += '/'

	elif path.endswith("/") and not trailing_slash:
		path = path[:-1]

	return path


class Router:
	"Stores and dispatches routes for an HTTP server"


	def __init__(self,
				name: str,
				register: bool = True,
				trailing_slash: bool = False,
				**types: TypeConverter) -> None:
		"""
			Create a new ``Router`` object

			:param name: Internal identifier
			:param register: Add this router to the global router list
			:param trailing_slash: Ensure paths end with ``/``
			:param types: Mapping of type names and their converter functions
		"""

		self.name: str = name
		"Internal identifier"

		self.routes: dict[str, BaseRoute] = {}
		"Routes handled by this router"

		self.trailing_slash: bool = trailing_slash
		"If ``True``, append a forward slash at the end of the path if doesn't end with one"

		self.types: dict[str, TypeConverter] = {
			"str": str,
			"bool": convert_to_boolean,
			"int": int,
			"float": float,
			"ts": lambda v: datetime.fromtimestamp(float(v))
		}
		"""
			Parameter types and the function to handle the conversion

			The function should be ``function(value: str) -> [type]``
		"""

		self.cache: dict[str, Match] = {}

		self.types.update(types)

		if register:
			Router.set(self)


	def __repr__(self) -> str:
		return f"Router('{self.name}', trailing_slash={self.trailing_slash})"


	@staticmethod
	def get(name: str, create: bool = False) -> Router:
		"""
			Get a router with the specified name

			:param name: Internal name of the router to get
			:param create: If ``True``, create a new router if it doesn't exist'=
			:raises KeyError: If ``create`` is ``False`` and a router cannot be found
		"""

		for router in ROUTERS:
			if router.name == name:
				return router

		if create:
			return Router(name, register = True)

		raise KeyError(name)


	@staticmethod
	def set(router: Router) -> None:
		"""
			Add a router to the global router list

			:raises KeyError: If a router by the same name exists
		"""

		try:
			Router.get(router.name)

		except KeyError:
			ROUTERS.append(router)
			return

		raise KeyError(router.name)


	def add_route(self, handler: RouteHandler, path: str, *methods: HttpMethod | str) -> BaseRoute:
		"""
			Add a route to be handled by the router

			:param handler: Function to be called for the route
			:param path: Path to handle
			:param methods: Methods to handle
		"""

		parsed_path = parse_path(path, self.trailing_slash)
		parsed_methods = [HttpMethod.parse(method) for method in methods]

		if not parsed_methods:
			parsed_methods.append(HttpMethod.GET)

		try:
			route = self.routes[parsed_path]

		except KeyError:
			route = Route.parse_path(path, self)
			self.routes[parsed_path] = route

		route.handlers.update({method: handler for method in parsed_methods})
		return route


	def add_file_route(self,
						directory: File | str,
						path: str,
						handler: RouteHandler) -> FileRoute:
		"""
			Add a route that serves static files

			:param directory: Base filesystem directory to use for returning paths
			:param path: Virtual path to handle
			:param handler: Function to be called for the route
		"""

		if not isinstance(path, File):
			path = File(path).resolve()

		route = FileRoute(self, directory, path, handler)
		self.routes[path] = route
		return route


	def del_route(self, path: str) -> None:
		"""
			Delete a route

			:param path: Path of the route
		"""

		del self.routes[path]


	def match(self, path: str, method: HttpMethod | str = HttpMethod.GET) -> Match:
		"""
			Parse a path from a request

			:param path: Path of the request
			:param method: Method of the request
			:raises HttpError: If the route could not be found or the route does not handle the
				method
		"""

		method = HttpMethod.parse(method)
		path = parse_path(path, self.trailing_slash)

		try:
			return self.routes[path].match(path, method)

		except KeyError:
			pass

		for route in self.routes.values():
			try:
				return route.match(path, method)

			except HttpError as e:
				if e.status == 404:
					continue

				raise e

		raise HttpError(404, path)


	def route(self,
			path: str,
			*methods: HttpMethod | str) -> Callable[[RouteHandler], RouteHandler]:
		"""
			Decorator for adding a new route

			:param path: Path to handle
			:param methods: Methods to handle
			:raises ValueError: A handler for the path exists
		"""

		def wrapper(func: RouteHandler) -> RouteHandler:
			self.add_route(func, path, *methods)
			return func

		return wrapper


	def file_route(self,
					path: str,
					directory: File | str) -> Callable[[RouteHandler], RouteHandler]:
		"""
			Decorator for adding file routes

			:param path: Path to handle
			:param directory: File path to search
		"""

		def wrapper(func: RouteHandler) -> RouteHandler:
			self.add_file_route(directory, path, func)
			return func

		return wrapper



class BaseRoute(ABC):
	"Base class for all route classes"

	router: Router
	"Router the route is associated with"

	handlers: dict[HttpMethod, RouteHandler]
	"Functions to be called for different HTTP methods for the route"

	path: str
	"Path the route will handle"

	regex: re.Pattern[str]
	"Regex pattern to use when matching paths"


	def __repr__(self) -> str:
		return f"{get_object_name(self)}('{self.path}')"


	@abstractmethod
	def match(self, path: str, method: HttpMethod | str = HttpMethod.GET) -> Match:
		"""
			Parse a path from a request

			:param path: Path of the request
			:param method: Method of the request
			:raises HttpError: If the route could not be found or the route does not handle the
				method
		"""
		...


class Route(BaseRoute):
	"Represents a route handler"


	def __init__(self,
				router: Router,
				path: str,
				path_regex: re.Pattern[str] | str,
				parts: dict[str, TypeConverter],
				handlers: dict[HttpMethod, RouteHandler]) -> None:
		"""
			Create a new route

			:param router: Router the route will be attached to
			:param methods: List of methods the route will handle
			:param path: Raw path the route will handle
			:param path_regex: Regex pattern to use when matching paths
			:param parts: Mapping of name/callable pairs for parsing url parameters
			:param handlers: Functions to be called for the route
		"""

		self.router = router
		"Router the route will be attached to"

		self.path = path
		"Raw path the route will handle"

		self.handlers: dict[HttpMethod, RouteHandler] = handlers
		"Functions to be called for different HTTP methods for the route"

		self.parts: dict[str, TypeConverter] = parts
		"Mapping of name/callable pairs for parsing url parameters"

		self.regex: re.Pattern[str] = re.compile(path_regex)
		"Regex pattern to use when matching paths"


	@classmethod
	def parse_path(cls: type[Self], path: str, router: Router) -> Self:
		"""
			Parse a path

			:param path: Path to parse
			:param trailing_slash: Make sure the path ends with a ``/``
		"""

		path = parse_path(path, router.trailing_slash)
		path_regex = str(path)
		parts = {}

		try:
			for key in re.findall("{" + r"([A-Za-z0-9_\-:]+)" + "}", path):
				param_str = f"{{{key}}}"
				name, _, param_type = key.partition(":")

				if not param_type:
					param_type = "str"

				if param_type.lower() == "float":
					path_regex = path_regex.replace(param_str, rf"(?P<{key}>[0-9.]+)")

				elif param_type.lower() == "int":
					path_regex = path_regex.replace(param_str, rf"(?P<{key}>[0-9]+)")

				else:
					path_regex = path_regex.replace(param_str, rf"(?P<{key}>[A-Za-z0-9_\-:@.%+]+)")

				parts[name] = router.types[param_type]

		except IndexError:
			pass

		return cls(router, path, path_regex, parts, {})


	def match(self, path: str, method: HttpMethod | str = HttpMethod.GET) -> Match:
		method = HttpMethod.parse(method)
		path = parse_path(path, self.router.trailing_slash)
		kwargs = {}

		if len(self.parts):
			if not (match := self.regex.fullmatch(path)):
				raise HttpError.NotFound(path)

			for key, value in match.groupdict(default = "").items():
				kwargs[key] = self.parts[key](value)

		else:
			if self.path != path:
				raise HttpError.NotFound(path)

		try:
			return Match(method, path, self.handlers[method], kwargs)

		except KeyError:
			raise HttpError.MethodNotAllowed(method) from None


class FileRoute(BaseRoute):
	"Route for static files"

	directory: File
	"Filesystem path to fetch files from"

	def __init__(self,
				router: Router,
				directory: File | str,
				path: str, handler: RouteHandler) -> None:
		"""
			Create a new static file route

			:param router: Router the route will be attached to
			:param directory: Filesystem path to fetch files from
			:param path: Virtual path to handle
			:param handler: Function to be called for the route
		"""

		if not isinstance(directory, File):
			directory = File(directory).resolve()

		if not directory.exists:
			raise FileNotFoundError(directory)

		if not directory.isdir:
			raise ValueError(f"Path is not a directory: {directory}")

		self.router = router
		self.path = path
		self.directory = directory
		self.regex = re.compile(f"{path}/" + r"(?P<file>.*)")
		self.handler = handler


	@property
	def handler(self) -> RouteHandler:
		"Function to be called for the route. Alias of ``BaseHandler.handlers[HttpMethod.GET]``"

		return self.handlers[HttpMethod.GET]


	@handler.setter
	def handler(self, value: RouteHandler) -> None:
		self.handlers[HttpMethod.GET] = value


	def match(self, path: str, method: str = "GET") -> Match:
		if HttpMethod.parse(method) is not HttpMethod.GET:
			raise HttpError.MethodNotAllowed(method)

		path = parse_path(path, self.router.trailing_slash)

		if not (match := self.regex.fullmatch(path)):
			raise HttpError.NotFound(path)

		file_path = Path(match.groupdict()["file"], normalize = True)
		filename = self.directory.join(file_path)

		if not filename.exists and not filename.isfile:
			raise HttpError.NotFound(path)

		return Match(method, path, self.handler, {"file": filename})


class Match:
	"Represents a path match"

	method: str
	"Method of the request"

	path: str
	"Path of the request"

	handler: RouteHandler
	"Function to be ran"

	params: dict[str, object]
	"Parsed url parameters"

	def __init__(self, method: str, path: str, handler: RouteHandler, kwargs: Any):
		"""
			Create a new match

			:param method: Method of the request
			:param path: Path of the request
			:param handler: Function to be ran
			:param params: Parsed url parameters
		"""

		self.method = method
		self.path = path
		self.handler = handler
		self.params = kwargs


	def __call__(self, *args: tuple[object], **kwargs: dict[str, object]) -> object:
		"""
			Call the handler with ``params`` as keyword arguments

			:param args: Arguments to pass to the handler
			:param kwargs: Keyword arguments to pass to the handler
		"""

		return self.handler(*args, **kwargs, **self.params)


	def __repr__(self) -> str:
		return f'Match("{self.method} {self.path}", handler="{get_object_name(self.handler)}")'
