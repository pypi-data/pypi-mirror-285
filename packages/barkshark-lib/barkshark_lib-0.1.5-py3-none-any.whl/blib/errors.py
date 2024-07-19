from __future__ import annotations

import inspect

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from .enums import HttpStatus

if TYPE_CHECKING:
	try:
		from typing import Self

	except ImportError:
		from typing_extensions import Self


class ErrorMeta(type):
	"Meta class that sets all integer properties to :class:`ErrorCode` objects"

	def __new__(meta_cls: type,
				name: str,
				bases: Sequence[type[Any]],
				properties: dict[str, Any]) -> type:

		for key in properties:
			if key.startswith("_"):
				continue

			value = properties[key]

			if isinstance(value, int):
				properties[key] = ErrorCode(value, key)

		return type.__new__(type, name, tuple(bases), properties)


class ErrorCode(int):
	"Represents an error code for an error domain"


	def __init__(self, code: int, name: str):
		"""
			Create a new ErrorCode object

			.. note:: This class should never be manually initiated

			:param code: Number to use for the error
		"""
		self.name = name
		"Name of the error code"

		self.cls: type[Error] | None = None


	def __new__(cls: type[Self], code: int, name: str) -> Self:
		return int.__new__(cls, code)


	def __set_name__(self, obj: Any, name: str) -> None:
		self.cls = obj


	def __get__(self, obj: Any, objtype: type[Any]) -> type[Any] | Self:
		if obj is None:
			return self

		return self


	def __repr__(self) -> str:
		return f"ErrorCode(code={int.__repr__(self)}, name={repr(self.name)})"


	def __call__(self, message: str) -> Any:
		"""
			Create a new error for the specified error code

			:param message: Text to pass with the error
		"""

		if self.cls is None:
			raise ValueError("Class is null")

		return self.cls(self, message)


class Error(Exception):
	"Base error class"


	def __init__(self, code: ErrorCode, message: str):
		"""
			Create a new error object

			:param code: Number of the error
			:param message: Text to pass with the error
		"""

		Exception.__init__(self, f"[{code.name}] {message}")

		self.code: ErrorCode = code
		"Code of the error"


	def __eq__(self, other: type[Error] | Error | ErrorCode | int) -> bool: # type: ignore[override]
		if inspect.isclass(other):
			return type(self) == other # noqa: E721

		if isinstance(other, Error):
			return self.__class__ == other.__class__

		if isinstance(other, (ErrorCode | int)):
			for key in dir(type(self)):
				value = getattr(self, key)

				if other == value:
					return True

		return False


	@property
	def domain(self) -> str:
		"Name of the error group"
		return self.__class__.__name__


class FileError(Error, metaclass = ErrorMeta):
	"Raised on errors involving files"

	NotFound: ErrorCode = 0 # type: ignore[assignment]
	"Raised when a file or directory could not be found"

	Found: ErrorCode = 1 # type: ignore[assignment]
	"Raised when a file or directory exists when it should not"

	IsDirectory: ErrorCode = 2 # type: ignore[assignment]
	"Raised when the path is a directory when it should not be"

	IsFile: ErrorCode = 3 # type: ignore[assignment]
	"Raised when the path is a file when it should not be"


class HttpError(Exception):
	"Error raised from a client or server response"


	def __init__(self,
				status: HttpStatus | int,
				message: str | None = None,
				headers: dict[str, str] | None = None) -> None:
		"""
			Create a new http error

			:param status: Status code of the error
			:param message: Body of the error
			:param headers: Headers of the error
		"""

		self.status = HttpStatus.parse(status)
		"Status code and reason"

		self.message = message or self.status.reason
		"Message body of the error"

		self.headers = headers or {}
		"Headers associated with the error"


	def __str__(self) -> str:
		return f"HTTP Error {self.status}: {self.message}"


	def __repr__(self) -> str:
		return f"HttpError(status={self.status}, message='{self.message}')"


	@classmethod
	def Continue(cls: type[Self], message: str | None = None) -> Self:
		"""
			Create a new HTTP error for the ``100`` status code

			:param message: Text message to include in the response body
		"""

		return cls(100, message, None)


	@classmethod
	def MovedPermanently(cls: type[Self], url: str) -> Self:
		"""
			Create a new HTTP error for the ``301`` status code

			:param url: Url to redirect the client to
		"""

		return cls(301, None, {"Location": url})


	@classmethod
	def Found(cls: type[Self], url: str) -> Self:
		"""
			Create a new HTTP error for the ``302`` status code

			:param url: Url to redirect the client to
		"""

		return cls(302, None, {"Location": url})


	@classmethod
	def SeeOther(cls: type[Self], url: str) -> Self:
		"""
			Create a new HTTP error for the ``303`` status code

			:param url: Url to redirect the client to
		"""

		return cls(303, None, {"Location": url})


	@classmethod
	def TemporaryRedirect(cls: type[Self], url: str) -> Self:
		"""
			Create a new HTTP error for the ``307`` status code

			:param url: Url to redirect the client to
		"""

		return cls(307, None, {"Location": url})


	@classmethod
	def PermanentRedirect(cls: type[Self], url: str) -> Self:

		"""
			Create a new HTTP error for the ``308`` status code

			:param url: Url to redirect the client to
		"""

		return cls(308, None, {"Location": url})


	@classmethod
	def BadRequest(cls: type[Self], message: str | None = None) -> Self:
		"""
			Create a new HTTP error for the ``400`` status code

			:param message: Text message to include in the response body
		"""

		return cls(400, message, None)


	@classmethod
	def Unauthorized(cls: type[Self], message: str | None = None) -> Self:
		"""
			Create a new HTTP error for the ``401`` status code

			:param message: Text message to include in the response body
		"""

		return cls(401, message, None)


	@classmethod
	def Forbidden(cls: type[Self], message: str | None = None) -> Self:
		"""
			Create a new HTTP error for the ``403`` status code

			:param message: Text message to include in the response body
		"""

		return cls(403, message, None)


	@classmethod
	def NotFound(cls: type[Self], message: str | None = None) -> Self:
		"""
			Create a new HTTP error for the ``404`` status code

			:param message: Text message to include in the response body
		"""

		return cls(404, message, None)


	@classmethod
	def MethodNotAllowed(cls: type[Self], message: str | None = None) -> Self:
		"""
			Create a new HTTP error for the ``405`` status code

			:param message: Text message to include in the response body
		"""

		return cls(405, message, None)


	@classmethod
	def NotAcceptable(cls: type[Self], message: str | None = None) -> Self:
		"""
			Create a new HTTP error for the ``406`` status code

			:param message: Text message to include in the response body
		"""

		return cls(406, message, None)


	@classmethod
	def Teapot(cls: type[Self], message: str | None = None) -> Self:
		"""
			Create a new HTTP error for the ``418`` status code

			:param message: Text message to include in the response body
		"""

		return cls(418, message, None)


	@classmethod
	def InternalServerError(cls: type[Self], message: str | None = None) -> Self:
		"""
			Create a new HTTP error for the ``500`` status code

			:param message: Text message to include in the response body
		"""

		return cls(500, message, None)


	@classmethod
	def NotImplemented(cls: type[Self], message: str | None = None) -> Self:
		"""
			Create a new HTTP error for the ``501`` status code

			:param message: Text message to include in the response body
		"""

		return cls(501, message, None)


	@classmethod
	def BadGateway(cls: type[Self], message: str | None = None) -> Self:
		"""
			Create a new HTTP error for the ``502`` status code

			:param message: Text message to include in the response body
		"""

		return cls(502, message, None)


	@classmethod
	def HttpVersionNotSupported(cls: type[Self], message: str | None = None) -> Self:
		"""
			Create a new HTTP error for the ``505`` status code

			:param message: Text message to include in the response body
		"""

		return cls(505, message, None)


class NamespaceImportError(Exception):
	"Raised when a key in the resource json file is missing"

	key: str
	"Name of the missing key"

	def __init__(self, key: str):
		"""
			Create a new NamespaceImportError

			:param key: Name of the missing key
		"""
		Exception.__init__(self, f"Resource json file missing key: {key}")
		self.key = key


class NamespaceMatchError(Exception):
	"""
		Raised when loading a resource json file and the include namespace does not match the
		namespace it's being imported into
	"""

	namespace: str
	"Namespace of files being imported into"

	json: str
	"Namespace specified in the json file"


	def __init__(self, namespace: str, json: str):
		"""
			Create a new NamespaceMatchError

			:param namespace: Namespace of the files being imported into
			:param json: Namespace specified in the json file
		"""
		Exception.__init__(self, f"Namespaces do not match: '{namespace}', '{json}'")
		self.namespace = namespace
		self.json = json


class SqlError(Exception):
	"Base error for Sql namespace"


class TooManyConnectionsError(SqlError):
	"""
		Raised when tying to open a database connection, but the max open connection count has been
		reached
	"""

	maximum: int
	"Max number of connections allow at the time of the exception"

	count: int
	"Number of active connections at the time of the exception"

	def __init__(self, maximum: int, count: int):
		SqlError.__init__(self, f"Max: {maximum}, Count: {count}")
		self.maximum = maximum
		self.count = count
