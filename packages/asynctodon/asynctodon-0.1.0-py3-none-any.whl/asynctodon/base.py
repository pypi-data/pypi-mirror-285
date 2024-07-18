from blib import Date
from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Self


CODE_REDIRECT: str = "urn:ietf:wg:oauth:2.0:oob"


class ApiDate(Date):
	"""
		``Date`` class for API objects
	"""

	FORMAT: str = "%Y-%m-%dT%H:%M:%S.%zZ"
	ALT_FORMATS: Sequence[str] = (
		"%Y-%m-%dT%H:%M:%SZ",
		"%Y-%m-%d"
	)


	@classmethod
	def parse(cls: type[Self], date: datetime | str | int | float) -> Self:
		"""
			Parse a unix timestamp or date string

			:param date: Data to be parsed
		"""

		if isinstance(date, cls):
			return date

		elif isinstance(date, datetime):
			return cls.fromisoformat(date.isoformat())

		elif isinstance(date, (int | float)):
			data = cls.fromtimestamp(float(date) if type(date) is int else date)

		else:
			data = cls.fromisoformat(date)

		if data.tzinfo is None:
			return data.replace(tzinfo = timezone.utc)

		return data.astimezone(tz = timezone.utc)
