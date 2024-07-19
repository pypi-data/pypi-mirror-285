from __future__ import annotations

import enum
import os
import re

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
	try:
		from typing import Self

	except ImportError:
		from typing_extensions import Self


HTTP_REASON_REGEX = re.compile('[A-Z][^A-Z]*')
MULTIPLIER = {
	"B": 1,
	"KiB": 1024,
	"MiB": 1024 ** 2,
	"GiB": 1024 ** 3,
	"TiB": 1024 ** 4,
	"PiB": 1024 ** 5,
	"EiB": 1024 ** 6,
	"ZiB": 1024 ** 7,
	"YiB": 1024 ** 8,
	"KB": 1000,
	"MB": 1000 ** 2,
	"GB": 1000 ** 3,
	"TB": 1000 ** 4,
	"PB": 1000 ** 5,
	"EB": 1000 ** 6,
	"ZB": 1000 ** 7,
	"YB": 1000 ** 8
}


class Enum(enum.Enum):
	":class:`enum.Enum` with a ``parse`` method"

	@classmethod
	def from_index(cls: type[Self], index: int) -> Self:
		"""
			Get the enum item at the specified index

			:param index: Index of the enum item to get
			:raises IndexError: If the index is out of range
		"""

		if index < 0:
			index = len(cls) + index

		for idx, value in enumerate(cls):
			if idx == index:
				return value

		raise IndexError(index)


	@classmethod
	def parse(cls: type[Self], data: Any) -> Self:
		"""
			Get an enum item by name or value

			:param data: Name or value
			:raises AttributeError: If an item could not be found
		"""

		if isinstance(data, cls):
			return data

		try:
			return cls[data]

		except KeyError:
			pass

		try:
			return cls(data)

		except ValueError:
			pass

		if isinstance(data, str):
			for item in cls:
				if issubclass(cls, StrEnum) and data.lower() == item.value.lower():
					return item

				if data.lower() == item.name.lower():
					return item

		raise AttributeError(f'Invalid enum property for {cls.__name__}: {data}')


class StrEnum(str, Enum):
	"Enum where items can be treated like a :class:`str`"

	def __str__(self) -> str:
		return self.value # type: ignore[no-any-return]


class IntEnum(enum.IntEnum, Enum):
	"Enum where items can be treated like an :class:`int`"


class IntFlagEnum(enum.IntFlag, Enum): # type: ignore[misc]
	":class:`IntEnum` with items that can be used like flags"


class FilePermField(IntFlagEnum):
	READ = 4
	WRITE = 2
	EXECUTE = 1

	R = READ
	W = WRITE
	X = EXECUTE


	@property
	def short_name(self) -> str:
		if self.value == 4:
			return "r"

		if self.value == 2:
			return "w"

		if self.value == 1:
			return "x"

		raise ValueError("heck")


class FileSizeUnit(StrEnum):
	"Unit identifier for various file sizes"

	BYTE = 'B'

	KIBIBYTE = 'KiB'
	MEBIBYTE = 'MiB'
	GIBIBYTE = 'GiB'
	TEBIBYTE = 'TiB'
	PEBIBYTE = 'PiB'
	EXBIBYTE = 'EiB'
	ZEBIBYTE = 'ZiB'
	YOBIBYTE = 'YiB'

	KILOBYTE = 'KB'
	MEGABYTE = 'MB'
	GIGABYTE = 'GB'
	TERABYTE = 'TB'
	PETABYTE = 'PB'
	EXABYTE = 'EB'
	ZETTABYTE = 'ZB'
	YOTTABYTE = 'YB'

	B = BYTE
	K = KIBIBYTE
	M = MEBIBYTE
	G = GIBIBYTE
	T = TEBIBYTE
	P = PEBIBYTE
	E = EXBIBYTE
	Z = ZEBIBYTE
	Y = YOBIBYTE


	@property
	def multiplier(self) -> int:
		"Get the multiplier for the unit"

		return MULTIPLIER[str(self)]


	def multiply(self, size: int | float) -> int | float:
		"""
			Multiply a file size to get the size in bytes

			:param size: File size to be multiplied
		"""
		return self.multiplier * size


class FileType(Enum):
	"File type"

	DIR = enum.auto()
	FILE = enum.auto()
	LINK = enum.auto()
	UNKNOWN = enum.auto()


class HttpMethod(StrEnum):
	"Valid HTTP methods"

	CONNECT = "connect"
	DELETE = "delete"
	GET = "get"
	HEAD = "head"
	OPTIONS = "options"
	PATCH = "patch"
	POST = "post"
	PUT = "put"
	TRACE = "trace"


class HttpStatus(IntEnum):
	"HTTP status codes"

	Continue = 100
	SwitchingProtocols = 101
	Processing = 102
	EarlyHints = 103

	Ok = 200
	Created = 201
	Accepted = 202
	NonAuthoritativeInformation = 203
	NoContent = 204
	Resetcontent = 205
	PartialContent = 206
	MultiStatus = 207
	AlreadyReported = 208
	ImUsed = 226

	MultipleChoices = 300
	MovedPermanently = 301
	Found = 302
	SeeOther = 303
	NotModified = 304
	UseProxy = 305
	TemporaryRedirect = 307
	PermanentRedirect = 308

	BadRequest = 400
	Unauthorized = 401
	PaymentRequired = 402
	Forbidden = 403
	NotFound = 404
	MethodNotAllowed = 405
	NotAcceptable = 406
	ProxyAuthenticationRequired = 407
	RequestTimeout = 408
	Conflict = 409
	Gone = 410
	LengthRequired = 411
	PreconditionFailed = 412
	RequestEntityTooLarge = 413
	RequestUriTooLong = 414
	UnsupportedMediaType = 415
	RequestRangeNotSatisfiable = 416
	ExpectationFailed = 417
	IAmATeapot = 418
	EnhanceYourCalm = 420
	TooHighToHandleYourShit = 420 # this will get removed in the future
	MisdirectedRequest = 421
	UnprocessableEntity = 422
	Locked = 423
	FailedDependency = 424
	TooEarly = 425
	UpgradeRequired = 426
	PreconditionRequired = 428
	TooManyRequests = 429
	RequestHeaderFieldsTooLarge = 431
	UnavailableForLegalReasons = 451

	InternalServerError = 500
	NotImplemented = 501
	BadGateway = 502
	ServiceUnavailable = 503
	GatewayTimeout = 504
	HttpVersionNotSupported = 505
	VariantAlsoNegotiates = 506
	InsufficientStorage = 507
	LoopDetected = 508
	NotExtended = 510
	NetworkAuthenticationRequired = 511


	@property
	def reason(self) -> str:
		"The text associated with the code"

		return " ".join(HTTP_REASON_REGEX.findall(self.name))


class ProtocolPort(IntEnum):
	"Protocol names and their associated default port"

	FILE = 0
	FTP = 21
	SSH = 22
	TELNET = 23
	SMTP = 25
	WHOIS = 43
	DNS = 53
	TFTP = 69
	GOPHER = 70
	HTTP = 80
	WS = 80
	NTP = 123
	XDMCP = 177
	IRC = 194
	IMAP = 220
	HTTPS = 443
	WSS = 443
	SMB = 445
	RTSP = 554
	SMTPS = 587
	IPP = 631
	DOT = 853
	RSYNC = 873
	FTPS = 990
	IMAPS = 993
	NFS = 1023
	GEMINI = 1965
	TITAN = GEMINI

	# various servers
	MYSQL = 3306
	PULSEAUDIO = 4713
	RTP = 5004
	RTCP = 5005
	POSTGRES = 5432
	MPD = 6600
	IRCS = 6697

	# game servers
	TERRARIA = 7777
	STARBOUND = 21025
	MINECRAFT = 25565
	MUMBLE = 64738


class SeekPosition(IntEnum):
	"Position to set the offset from when seeking a buffer"

	START = os.SEEK_SET
	CURRENT = os.SEEK_CUR
	END = os.SEEK_END


class XdgDir(StrEnum):
	"XDG directories and their associated environmental variables"

	CACHE = "XDG_CACHE_HOME"
	CONFIG = "XDG_CONFIG_HOME"
	DATA = "XDG_DATA_HOME"
	RUNTIME = "XDG_RUNTIME_DIR"
	STATE = "XDG_DATA_STATE"


	@property
	def path(self) -> str:
		"Get the directory associated with the enum item"

		if os.name != "posix":
			raise RuntimeError("This method can only be used on POSIX systems")

		xdg_dir = {
			"XDG_CACHE_HOME": "~/.cache",
			"XDG_CONFIG_HOME": "~/.config",
			"XDG_DATA_HOME": "~/.local/share",
			"XDG_RUNTIME_DIR": f"/run/user/{os.getuid()}",
			"XDG_DATA_STATE": "~/.local/state"
		}

		return os.environ.get(self.value, os.path.expanduser(xdg_dir[self.value]))
