import asyncio
import json

from aiohttp import ClientResponseError, ClientSession, ClientTimeout, FormData
from blib import File, JsonBase, Query, Url, get_object_name
from collections.abc import AsyncIterator, Mapping, Sequence
from io import IOBase
from typing import Any, Self, TypeVar, Union, overload
from yarl import URL

from . import api
from .base import CODE_REDIRECT
from .enums import StreamEventType
from .errors import ClientError, ServerError
from .objects import Application, ListDeserializer, ObjectBase


C = TypeVar("C", bound = Union[JsonBase, ObjectBase])


class Client(ClientSession, api.AccountBase, api.AppBase, api.FilterBase, api.InstanceBase,
			api.MiscBase, api.NotificationBase, api.StatusBase, api.StreamBase, api.TagBase,
			api.TimelineBase):
	"Client for the Mastodon API."

	def __init__(self,
				host: str,
				token: str | None = None,
				name: str | None = None,
				website: Url | str | None = None,
				redirect_uri: Url | str | None = None,
				client_id: str | None = None,
				client_secret: str | None = None,
				scopes: Sequence[str] | None = None,
				timeout: int | float = 5,
				stream_timeout: int | float = 60,
				https: bool = True) -> None:
		"""
			Create a new ``Client`` object

			:param host: Hostname to connect to
			:param token: Client token to pass to authenticated endpoints
			:param name: Name to be used in the ``User-Agent`` header and when registering the
				application
			:param website: Website of the application
			:param redirect_uri: Location to redirect to when authenticating a user
			:param client_id: Client identifier from a previous application registration
			:param client_secret: Client secret from a previous application registration
			:param scopes: API scopes the application will use
			:param timeout: Number of seconds to wait for requests before giving up
			:param stream_timeout: Number of seconds to wait for a message or heartbeat on
				streaming endpoints
			:param https: Use ``https`` instead of ``http``
		"""

		self._timeout = ClientTimeout(total = float(timeout))

		ClientSession.__init__(
			self,
			auto_decompress = True,
			raise_for_status = False,
			timeout = self._timeout,
			trust_env = True,
			headers = {
				"User-Agent": name or "Asynctodon"
			}
		)

		self.https: bool = https
		self.host = host
		self.token: str | None = token
		self.name: str | None = name
		self.website: Url | None = website if website is None else Url.parse(website)
		self.redirect_uri: str = redirect_uri or CODE_REDIRECT
		self.client_id: str | None = client_id
		self.client_secret: str | None = client_secret
		self.scopes: list[str] = ["read"] if scopes is None else list(scopes)
		self.stream_timeout: int | float = stream_timeout


	@classmethod
	def new_from_app(cls: type[Self],
					app: Application,
					host: str,
					token: str | None = None) -> Self:
		"""
			Create a new ``Client`` from an ``Application``

			:param app: Application info to use
			:param host: Instance to connect to
			:param token: Access token to use
		"""

		client = cls(host, token)
		client.set_details_from_app(app)
		return client


	@property
	def host(self) -> str:
		"Instance the client will send requests to"

		return self._base_url.host # type: ignore[return-value,union-attr]


	@host.setter
	def host(self, value: str) -> None:
		if "/" in value:
			raise ValueError("Host must not contain path segments")

		self._base_url = URL(f"{'https' if self.https else 'http'}://{value}")


	def set_details_from_app(self, app: Application) -> None:
		"""
			Set application details from an ``Application`` object

			:param app: Application to set details from
		"""

		self.name = app.name
		self.website = app.website
		self.redirect_url = app.redirect_uri or CODE_REDIRECT
		self.client_id = app.client_id
		self.client_secret = app.client_secret
		self.scopes = app.scope or ["read"]


	@overload
	async def send(self,
				method: str,
				path: str,
				cls: type[C],
				data: Mapping[str, Any] | Sequence[Any] | None = None,
				query: Query | Mapping[str, str] | None = None,
				form: Mapping[str, Any] | None = None,
				token: bool = True) -> C:
		...


	@overload
	async def send(self,
				method: str,
				path: str,
				cls: ListDeserializer[C],
				data: Mapping[str, Any] | Sequence[Any] | None = None,
				query: Query | Mapping[str, str] | None = None,
				form: Mapping[str, Any] | None = None,
				token: bool = True) -> list[C]:
		...


	@overload
	async def send(self,
				method: str,
				path: str,
				cls: None,
				data: Mapping[str, Any] | Sequence[Any] | None = None,
				query: Query | Mapping[str, str] | None = None,
				form: Mapping[str, Any] | None = None,
				token: bool = True) -> None:
		...


	async def send(self,
				method: str,
				path: str,
				cls: type[C] | ListDeserializer[C] | None,
				data: Mapping[str, Any] | Sequence[Any] | None = None,
				query: Query | Mapping[str, str] | None = None,
				form: Mapping[str, Any] | None = None,
				token: bool = True) -> C | list[C] | None:
		"""
			Send a request to the instance

			:param method: HTTP method of the endpoint
			:param path: Path of the endpoint
			:param cls: Class to use when parsing returned data. Use ``None`` if not expecting a
				response.
			:param data: JSON data to send with the request. Do not use with ``form``.
			:param query: Query parameters to append to the url
			:param form: HTML form data to send with the request. Do not use with ``data``.
			:param token: Ensure a token is set before sending the request
		"""

		open_files: list[IOBase] = []
		headers: dict[str, str] = {
			"Accept": "application/json"
		}

		if self.token is None:
			if token:
				raise ClientError(f"Token required for endpoint: {method} {path}")

		else:
			headers["Authorization"] = f"Bearer {self.token}"

		body: str | bytes | FormData | None = None

		try:
			if form is not None:
				body = FormData()

				for key, value in form.items():
					if isinstance(value, File):
						value = value.resolve()
						open_files.append(open(value, "rb"))

						body.add_field(key, open_files[-1], filename = value.name)

					else:
						body.add_field(key, value)

			elif data is not None:
				headers["Content-Type"] = "application/json"
				body = data.to_json() if isinstance(data, JsonBase) else json.dumps(data)

			request = self.request(
				method,
				path,
				params = query,
				data = body,
				headers = headers
			)

			async with request as resp:
				if resp.status >= 400:
					if resp.content_type == "application/json":
						msg = await resp.json()
						text = msg.get("error_description", msg["error"])
						raise ServerError(resp.status, text)

					# this should never get called, but keeping here just in case
					if resp.content_type == "text/html":
						raise ServerError(resp.status, resp.reason or "")

					raise ServerError(resp.status, await resp.text())

				if cls is not None:
					try:
						if type(cls) is ListDeserializer:
							return cls(await resp.json())

						if type(cls) is type and issubclass(cls, (ObjectBase, JsonBase)):
							return cls.parse(await resp.json()) # type: ignore[return-value]

						raise ValueError(f"Invalid parser class: {get_object_name(cls)}")

					except ClientResponseError:
						raise ClientError(f"No response returned for endpoint '{path}'")

		finally:
			for file in open_files:
				file.close()

		return None


	async def stream(self,
				path: str,
				query: Mapping[str, str] | None = None) -> AsyncIterator[api.StreamEvent]:
		"""
			Connect to a streaming endpoint and return an iterator of events

			:param path: Path to the streaming endpoint
			:param query: Query parameters to append to the url
		"""

		headers: dict[str, str] = {
			"Accept": "application/json",
			"Authorization": f"Bearer {self.token}"
		}

		if query is None:
			query = {}

		async with self.request("GET", path, params = query, headers = headers, timeout = 0.0) as r:
			event_name: str | None = None

			while True:
				line = await asyncio.wait_for(r.content.readline(), timeout = self.stream_timeout)

				if line.startswith(b"event:"):
					event_name = line.split(b":", 1)[1].decode("utf-8").strip()

				elif line.startswith(b"data:") and event_name is not None:
					yield api.StreamEvent(
						StreamEventType.parse(event_name),
						JsonBase.parse(line.split(b":", 1)[1].decode("utf-8"))
					)

					event_name = None
