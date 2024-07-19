from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone, tzinfo
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	try:
		from typing import Self

	except ImportError:
		from typing_extensions import Self


class Date(datetime):
	"""
		``datetime`` object with convenience methods for parsing and creating date strings. All
		objects assume a ``UTC`` timezone if one is not specified.
	"""

	FORMAT: str = "%d/%m/%Y %H:%M:%S %Z"
	"Format to pass to datetime when (de)serializing a raw date string"

	ALT_FORMATS: Sequence[str] = []
	"Extra formats to be used when deserializing a raw date string"

	LOCAL: tzinfo = datetime.now().astimezone().tzinfo # type: ignore[assignment]
	"Local timezone for the machine"

	UTC: tzinfo = timezone.utc
	"UTC timezone"


	def __new__(cls: type[Self],
				year: int,
				month: int,
				day: int,
				hour: int = 0,
				minute: int = 0,
				second: int = 0,
				microsecond: int = 0,
				tzinfo: tzinfo = timezone.utc) -> Self:

		return datetime.__new__(
			cls, year, month, day, hour, minute, second, microsecond, tzinfo
		)


	def __str__(self) -> str:
		return self.to_string()


	@classmethod
	def parse(cls: type[Self], date: datetime | str | int | float, try_iso: bool = True) -> Self:
		"""
			Parse a unix timestamp or HTTP date in string format

			:param date: Data to be parsed
		"""

		data: Self | None = None

		if isinstance(date, cls):
			return date

		elif isinstance(date, datetime):
			return cls.fromisoformat(date.isoformat())

		elif isinstance(date, (int | float)):
			data = cls.fromtimestamp(float(date) if type(date) is int else date, cls.UTC)

		else:
			for fmt in [cls.FORMAT, *cls.ALT_FORMATS]:
				try:
					data = cls.strptime(date, fmt)

				except ValueError:
					pass

			if try_iso:
				return cls.fromisoformat(date)

			if data is None:
				raise ValueError(f"Value cannot be parsed by {cls.__name__}: {repr(date)}")

		if data.tzinfo is None:
			return data.replace(tzinfo = cls.UTC)

		return data.astimezone(tz = cls.UTC)


	@classmethod
	def new_utc(cls: type[Self]) -> Self:
		"Create a new ``Date`` object from the current UTC time"

		return cls.now(cls.UTC)


	@classmethod
	def new_local(cls: type[Self]) -> Self:
		"Create a new ``Date`` object from the current local time"

		return cls.now(cls.LOCAL)


	def timestamp(self) -> int:
		"Return the date as a unix timestamp without microseconds"

		return int(datetime.timestamp(self))


	def to_string(self) -> str:
		"Create a date string in the format specified in ``Date.FORMAT``"

		return self.strftime(self.FORMAT)


class HttpDate(Date):
	"A ``Date`` class for parsing and creating date strings used in HTTP headers"

	FORMAT: str = "%a, %d %b %Y %H:%M:%S %Z"
	"Format to pass to datetime when (de)serializing a raw HTTP date"
