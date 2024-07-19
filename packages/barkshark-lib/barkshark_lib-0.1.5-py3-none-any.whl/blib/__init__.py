__software__ = "Barkshark Lib"
__version_info__ = (0, 1, 5)
__version__ = ".".join(str(v) for v in __version_info__)
__author__ = "Zoey Mae"
__homepage__ = "https://git.barkshark.xyz/barkshark/blib"


from .application import Application
from .date import Date, HttpDate
from .transport import AsyncTransport, aprint

from .enums import (
	Enum,
	IntEnum,
	IntFlagEnum,
	StrEnum,
	FilePermField,
	FileSizeUnit,
	FileType,
	HttpMethod,
	HttpStatus,
	ProtocolPort,
	SeekPosition,
	XdgDir
)

from .errors import (
	Error,
	ErrorCode,
	ErrorMeta,
	FileError
)

# todo: convert these errors to use the new Error class
from .errors import (
	HttpError

)

from .icon_theme import (
	FileIconTheme,
	Icon,
	IconTheme,
	IconThemes,
	MemoryIconTheme
)

from .misc import (
	catch_errors,
	convert_to_boolean,
	convert_to_bytes,
	convert_to_string,
	deprecated,
	get_object_name,
	get_object_properties,
	get_resource_path,
	get_top_domain,
	http_request,
	is_loop_running,
	random_str,
	time_function,
	time_function_pprint,
	ClassProperty,
	DictProperty,
	Env,
	FileSize,
	JsonBase,
	NamedTuple,
	RunData,
	StaticProperty
)

from .objects import (
	Object,
	Property,
	Signal,
	SignalObj
)

from .path import (
	AsyncFile,
	File,
	Path,
	UnixPerms
)

from .router import (
	Match,
	Route,
	Router
)

from .url import (
	Query,
	Url
)
