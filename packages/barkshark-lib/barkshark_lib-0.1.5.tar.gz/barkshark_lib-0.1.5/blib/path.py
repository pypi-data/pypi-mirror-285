from __future__ import annotations

import asyncio
import atexit
import os
import platform
import shutil
import sys

from collections.abc import AsyncIterator, Awaitable, Callable, Iterator, Sequence
from concurrent.futures import Executor, ThreadPoolExecutor
from functools import partial
from glob import iglob
from io import IOBase
from typing import TYPE_CHECKING, Any, IO, NamedTuple, ParamSpec, TypeVar

from .date import Date
from .enums import FilePermField, FileType, SeekPosition, XdgDir
from .errors import FileError
from .misc import FileSize, convert_to_bytes, deprecated

if TYPE_CHECKING:
	try:
		from typing import Self

	except ImportError:
		from typing_extensions import Self


COMPRESSION_EXT = ("br", "bz2", "gz", "lz", "lz4", "lzma", "lzo", "rz", "sz", "xz", "z", "zst")

T = TypeVar("T")
P = ParamSpec("P")


class UnixPerms(NamedTuple):
	"Represents a file's unix permission octal"

	user: int
	group: int
	other: int


	def __int__(self) -> int:
		return int("".join(str(perm) for perm in self), 8)


	def __str__(self) -> str:
		values = "".join(str(perm) for perm in self)
		return f"0o{values}"


	@classmethod
	def parse(cls: type[Self], data: UnixPerms | int | str, _st_mode: bool = False) -> Self:
		"""
			Convert a ``str`` or ``int`` to a ``UnixPerms`` object

			:param data: Object to convert
			:param _st_mode: Internal use
		"""

		if isinstance(data, cls):
			return data

		if isinstance(data, int):
			if _st_mode:
				return cls(*(str(oct(data))[-3:]))

			try:
				data = int(str(data), 8)

			except ValueError:
				pass

			data = format(data, 'o')
			return cls(*(int(n) for n in data))

		if isinstance(data, str):
			# octal as a string (0o644)
			if data.startswith("0o"):
				data = data[2:]

			# permission octals (1644 or 666)
			if data.isdigit():
				if len(data) == 4:
					data = data[1:]

				elif len(data) != 3:
					raise ValueError("Invalid permission octal")

				return cls(*(int(v) for v in data))

			# ls string (-rw-r--r--)
			if len(data) == 10:
				data = data[1:]

			elif len(data) != 9:
				raise ValueError("Invalid permission string")

			return cls(
				cls._str_to_int(data[0:3]),
				cls._str_to_int(data[3:6]),
				cls._str_to_int(data[6:9])
			)

		raise TypeError('Data must be an int, oct, or str')


	@classmethod
	def directory(cls: type[Self]) -> Self:
		"Create a new ``UnixPerms`` object with the recommended values for a directory"

		return cls(7, 5, 5)


	@classmethod
	def file(cls: type[Self]) -> Self:
		"Create a new ``UnixPerms`` object with the recommended values for a file"

		return cls(6, 4, 4)


	@staticmethod
	def _int_to_str(value: int) -> str:
		new_value = ''

		for item in FilePermField:
			if item.value <= value:
				new_value += item.short_name
				value -= item.value

			else:
				new_value += "-"

		return new_value


	@staticmethod
	def _str_to_int(string: str) -> int:
		new_value = 0

		for value in string:
			if value == "-":
				continue

			new_value += FilePermField.parse(value.upper())

		return new_value


	def to_int(self) -> int:
		"Return the permissions as an integer"

		return int(self)


	def to_string(self) -> str:
		"Return the permissions as a string representation of an octal"

		return str(self)



class Path(str):
	"Represents a path"

	def __init__(self, path: str, normalize: bool = False) -> None:
		"""
			Create a new ``Path`` object

			:param path: Path to manage
			:param normalize: Parse a path to remove unecessary and redundant segments
		"""


	def __new__(cls: type[Self], path: str, normalize: bool = False) -> Self:
		if normalize:
			path = os.path.normpath(path)

		return str.__new__(cls, path)


	def __repr__(self) -> str:
		return f"{self.__class__.__name__}('{str(self)}')"


	@property
	def ext(self) -> str:
		"Get the extension if one exists"

		parts = self.name.split(".")

		if len(parts) == 1:
			return ""

		if len(parts) == 2:
			return parts[1]

		if parts[-1].lower() in COMPRESSION_EXT:
			return ".".join(parts[-2:])

		return parts[-1]


	@property
	def name(self) -> str:
		"Return the last path segment"

		return os.path.basename(self)


	@property
	def parent(self) -> Self:
		"Remove the last path segment"

		return self.__class__(os.path.dirname(self))


	@property
	def stem(self) -> str:
		"Return the name without the extension"

		return self.name.rstrip(self.ext).rstrip(".")


	def join(self, *parts: str, normalize: bool = False) -> Self: # type: ignore[override]
		"""
			Append a path segment

			:param parts: Path segments to append
			:param normalize: Normalize the path before returning it
		"""

		return self.__class__(os.path.join(self, *parts), normalize = normalize)


	def normalize(self) -> Self:
		"Remove unecessary and redundant segments"

		return self.__class__(self, True)


class File(Path):
	"Represents a file on the local filesystem"

	exist_ok: bool = True
	"If ``True``, don't raise an exception when the file or directory does exist"

	missing_ok: bool = True
	"If ``True``, don't raise an exception when the file or directory doesn't exist"

	parents: bool = True
	"If ``True``, don't raise an exception when the parent directory doesn't exist"


	def __init__(self, path: str, normalize: bool = True) -> None:
		"""
			Create a new ``File`` object

			:param path: Path to the file or directory
			:param normalize: Parse a path to remove unecessary and redundant segments
		"""

		Path.__init__(self, path, normalize = normalize)


	@classmethod
	def cwd(cls: type[Self]) -> Self:
		"Create a new :class:`Path` from the current working directory"

		return cls(".").resolve()


	@classmethod
	def home(cls: type[Self]) -> Self:
		"Create a new :class:`Path` from the current user home directory"

		return cls("~").resolve()


	@classmethod
	def script(cls: type[Self]) -> Self:
		"Create a new :class:`Path` from the currently executed script"

		try:
			path = getattr(sys.modules["__main__"], "__file__")

		except Exception:
			path = sys.argv[0]

		return cls(path).resolve().parent


	@classmethod
	def xdg(cls: type[Self], dir_type: XdgDir | str) -> Self:
		"""
			Create a new :class:`Path` for an XDG directory

			:param dir_type: XDG name
		"""

		return cls(XdgDir.parse(dir_type).path)


	@property
	def atime(self) -> Date:
		"Get the date of the last access"

		return Date.parse(os.path.getatime(self))


	@property
	def ctime(self) -> Date:
		"Get the file creation date"

		return Date.parse(os.path.getctime(self))


	@property
	def exists(self) -> bool:
		"Check if the path exists"

		return os.path.exists(self)


	@property
	def isdir(self) -> bool:
		"Check if the path is a directory"

		return os.path.isdir(self)


	@property
	def isfile(self) -> bool:
		"Check if the path is a file"

		return os.path.isfile(self)


	@property
	def islink(self) -> bool:
		"Check if the path is a symlink"

		return os.path.islink(self)


	@property
	def isabsolute(self) -> bool:
		"Check if the path is absolute"

		return os.path.isabs(self)


	@property
	def mtime(self) -> Date:
		"Get the date of the last modification"

		return Date.parse(os.path.getmtime(self))


	@property
	def permissions(self) -> UnixPerms:
		return UnixPerms.parse(os.stat(self).st_mode, _st_mode = True)


	@property
	def size(self) -> FileSize:
		"Get the size of the path or directory"

		return FileSize(os.path.getsize(self))


	def chmod(self, mode: UnixPerms | int | str) -> None:
		"""
			Change UNIX file permissions

			:param mode: File permission mode to set
		"""

		os.chmod(self, UnixPerms.parse(mode).to_int(), follow_symlinks = False)


	def delete(self) -> None:
		"Delete the file or directory"

		if self.isdir:
			shutil.rmtree(self)

		else:
			os.remove(self)


	def get_types(self) -> tuple[FileType, ...]:
		"Get all the types of the path"

		types = []

		if self.isfile:
			types.append(FileType.FILE)

		elif self.isdir:
			types.append(FileType.DIR)

		else:
			types.append(FileType.UNKNOWN)

		if self.islink:
			types.append(FileType.LINK)

		return tuple(types)


	def glob(self,
			pattern: str = "**",
			recursive: bool = False,
			hidden: bool = False,
			ext: Sequence[str] | None = None) -> Iterator[File]:
		"""
			Iterate through a directory with paths matching a specific pattern

			.. note:: See :class:`glob.iglob` for pattern usage

			:param pattern: Filename pattern to match
			:param recursive: Whether or not to search through sub-directories
			:param hidden: List hidden files
			:param ext: Include only the specified extensions in the result if set
			:raises FileError: If the path is not a directory or does not exist
		"""

		if self.isfile:
			raise FileError.IsFile(self)

		if not self.exists:
			raise FileError.NotFound(self)

		for path in iglob(pattern, root_dir = self, recursive = recursive, include_hidden = hidden):
			filepath = self.join(path)

			if ext is None or filepath.ext in ext:
				yield filepath


	def mkdir(self, mode: UnixPerms | int | str = UnixPerms.directory()) -> None:
		"""
			Create a directory and all parent directories

			:param mode: Unix permission flags to set for the new directories
		"""

		os.makedirs(self, mode = int(UnixPerms.parse(mode)), exist_ok = self.exist_ok)


	def open(self, mode: str = "r") -> IO[Any]:
		"""
			Open the file for reading and/or writing

			:param mode: Read/write mode to open the file as
		"""

		return open(self, mode)


	def open_async(self) -> AsyncFile:
		"Open the file for reading and writing via async"

		return AsyncFile(self)


	def read(self) -> bytes:
		"Return the raw contents of the file"

		with open(self, "rb") as fd:
			return fd.read()


	def read_text(self, encoding: str = "utf-8") -> str:
		"Return the contents of the file as text"

		return self.read().decode(encoding)


	def remove(self) -> None:
		"Delete the file or directory"

		if self.islink or self.isfile:
			os.remove(self)

		elif not self.isdir:
			raise ValueError("File is not a file, directory, or symlink")

		if self.parents:
			shutil.rmtree(self)

		else:
			os.rmdir(self)


	def resolve(self) -> Self:
		"Replace `~` with the current user home and follow any symlinks in the path"

		path = str(self)

		if self.startswith("~"):
			path = os.path.expanduser(path)

		return type(self)(os.path.realpath(path, strict = False))


	def relative_to(self, path: Path) -> str:
		"""
			Get the a path segment relative to another path

			:param path: Path to use as the base directory
			:raises ValueError: When the path is not a child of the specified path
		"""

		if not self.startswith(path):
			raise ValueError("This path is not relative to the specified path")

		return self.replace(path if path.endswith("/") else f"{path}/", "")


	def symlink_from(self, src: File) -> None:
		"""
			Create a symlink at the current path from another path

			:param src: Path to link to
		"""

		src = src.resolve()
		os.symlink(src, self, target_is_directory = src.isdir)


	def touch(self,
			size: int = 0,
			mode: UnixPerms | int | str = UnixPerms.file(),
			dir_mode: UnixPerms | int | str = UnixPerms.directory(),
			overwrite: bool = False) -> None:
		"""
			Create an empty file

			:param size: Size in bytes to make the file
			:param mode: Unix permissions to set on the file if not running Windows
			:param dir_mode: Unix permissions to set on newly created parent directories if not
				running windows
		"""

		if self.exists:
			if not overwrite:
				raise FileExistsError(self)

			self.delete()

		if self.parents:
			self.resolve().parent.mkdir(dir_mode)

		with open(self, "bw+") as fd:
			if size > 0:
				fd.seek(size - 1)
				fd.write(b"\0")

			else:
				fd.write(b"")

		if platform.system() != "Windows":
			self.chmod(mode)


	def write(self, data: bytes | str, overwrite: bool = True, encoding: str = "utf-8") -> None:
		"""
			Write data to a file

			:param data: Data to write
			:param overwrite: Replaces the contents of the file if set to ``True``, otherwise it
				gets appended to the end of the file.
			:param encoding: Encoding to use when converting ``str`` data
		"""

		if isinstance(data, str):
			data = data.encode(encoding)

		with open(self, "bw+" if overwrite else "bw") as fd:
			fd.write(data)


class AsyncFile:
	"Opens a file for reading and writing with async. Can be used as a context manager."


	def __init__(self, path: File | Path | str) -> None:
		"""
			Asyncronously open a file

			:param path: Filesystem path to the file
		"""

		if isinstance(path, Path):
			path = File(str(path))

		elif isinstance(path, str):
			path = File(path)

		self._path = path
		self._fp: IOBase | None = None
		self._loop: asyncio.AbstractEventLoop | None = None
		self._executor: Executor | None = None

		atexit.register(self._close)


	def __del__(self) -> None:
		atexit.unregister(self._close)


	async def __aenter__(self) -> Self:
		await self.open()
		return self


	async def __aexit__(self, *args: Any) -> None:
		await self.close()


	@property
	def opened(self) -> bool:
		"Return ``True`` if the file is currently open"

		return self._fp is not None


	@property
	def path(self) -> File:
		"Filesystem path to the file"

		return self._path


	@property
	def position(self) -> int:
		"Return the current position of the buffer cursor"

		if self._fp is None:
			raise asyncio.InvalidStateError("File is not open")

		return self._fp.tell()


	async def close(self) -> None:
		"Close the file for reading and writing. Can be safely called multiple times."

		if self._loop is None or self._executor is None or self._fp is None:
			return

		await self._exec(self._fp.close)

		self._executor.shutdown()
		self._executor = None
		self._fp = None


	async def open(self) -> None:
		"Open the file for reading and writing. Can be safely called multiple times."

		if self._loop is None:
			self._loop = asyncio.get_running_loop()

		if self._executor is None:
			self._executor = ThreadPoolExecutor()

		if self._fp is None:
			self._fp = await self._exec(open, self.path, "ba+")


	async def read(self, length: int = -1, seek_start: bool = False) -> bytes:
		"""
			Read data from the file at the current position and seek back to the start.

			:param length: Number of bytes to read. Reads the entire file by default.
			:param seek_start: Seek to the start of the buffer before reading data.
		"""

		if self._fp is None:
			raise asyncio.InvalidStateError("File is not open")

		if seek_start:
			self.seek_to_start()

		return await self._exec(self._fp.read, length)


	async def read_line(self, size: int = -1) -> bytes:
		"""
			Read a line with the maximum number of bytes specified by ``size``

			:param size: Maximum number of bytes to return
			:raises IOError: When ``size`` is above 0 and the length of the returned data is longer
				than the specified size.
		"""

		if self._fp is None:
			raise asyncio.InvalidStateError("File is not open")

		data = await self._exec(self._fp.readline, size)

		if size > 0 and not data.endswith((b"\r", b"\n")) and len(data) == size:
			raise IOError(f"Line is longer than {size} bytes")

		return data


	async def read_lines_iterator(self,
								size: int = -1,
								seek_start: bool = True) -> AsyncIterator[bytes]:
		"""
			Read an array of lines that have a maximum length specified by ``size``

			:param size: Maximum number of bytes for each line
			:param seek_start: Seek to the start of the buffer before reading data.
			:raises IOError: When ``size`` is above 0 and the length of a line is longer than the
				specified size.
		"""

		if seek_start:
			self.seek_to_start()

		while True:
			if len(data := await self.read_line()) == 0:
				break

			yield data


	async def read_lines(self, size: int = -1, seek_start: bool = True) -> list[bytes]:
		"""
			Read an array of lines that have a maximum length specified by ``size``

			:param size: Maximum number of bytes for each line
			:param seek_start: Seek to the start of the buffer before reading data.
			:raises IOError: When ``size`` is above 0 and the length of a line is longer than the
				specified size.
		"""

		lines = []

		async for line in self.read_lines_iterator(size, seek_start):
			lines.append(line)

		return lines


	async def read_text(self,
						length: int = -1,
						encoding: str = "utf-8",
						seek_start: bool = False) -> str:
		"""
			Read data from the file at the current position as text and seek back to the start.

			:param length: Number of bytes to read. Reads the entire file by default.
			:param encoding: Text encoding to use when decoding.
			:param seek_start: Seek to the start of the buffer before reading data.
		"""

		return (await self.read(length, seek_start)).decode(encoding)


	async def write(self, data: Any, encoding: str = "utf-8", flush: bool = True) -> None:
		"""
			Write data to the file starting with the current position (usually the start of the file)

			:param data: Data to be written. Will be converted to bytes if possible.
			:param encoding: Encoding to use when converting non-bytes objects.
			:param flush: Also flush the buffers.
		"""

		if self._fp is None:
			raise asyncio.InvalidStateError("File is not open")

		await self._exec(self._fp.write, convert_to_bytes(data, encoding))

		if flush:
			await self._exec(self._fp.flush)


	async def write_lines(self, data: Sequence[Any], separator: Any = b"") -> None:
		"""
			Write an array of data to the file separated by ``separator``

			:param data: Array of data to be written. Each item will get converted to bytes
				if possible.
			:param separator: Data to write between each item.
		"""

		last_id = len(data) - 1

		for idx, line in enumerate(data):
			if idx == last_id:
				await self.write(line, flush = True)
				return

			await self.write(line, flush = False)

			if separator:
				await self.write(separator, flush = False)


	def seek(self, offset: int, whence: SeekPosition | int = SeekPosition.CURRENT) -> None:
		"""
			Change the current file buffer position

			:param offset: Number of bytes to change the position by
			:param whence: Position to start the offset from
		"""

		if self._fp is None:
			raise asyncio.InvalidStateError("File is not open")

		self._fp.seek(offset, SeekPosition.parse(whence))


	@deprecated("File.seek_to_start", "0.1.4", "0.2.0")
	def seek_to_beginning(self) -> None:
		"Alias for :meth:`File.seek_to_start` (to be removed in 0.2.0)"

		self.seek_to_start()


	def seek_to_start(self) -> None:
		"Seek to the start of the file"

		self.seek(0, SeekPosition.START)


	def seek_to_end(self) -> None:
		"Seek to the end of the file"

		self.seek(0, SeekPosition.END)


	def _close(self) -> None:
		if self._fp is not None:
			self._fp.close()

		if self._executor is not None:
			self._executor.shutdown()


	def _exec(self, callback: Callable[P, T], *args: Any, **kwargs: Any) -> Awaitable[T]:
		if self._loop is None or self._executor is None:
			raise asyncio.InvalidStateError("Loop or executor is not active")

		return self._loop.run_in_executor(self._executor, partial(callback, *args, **kwargs))
