from __future__ import annotations

from blib import JsonBase, Url, get_object_name
from collections.abc import Callable, Mapping, Sequence
from copy import deepcopy
from typing import Any, Generic, Self, TypeVar, overload

from .base import ApiDate
from .errors import InvalidFieldError

from .enums import (
	BlockSeverity,
	FilterAction,
	ListReplyPolicy,
	MediaType,
	NotificationType,
	PermissionFlag,
	PreviewCardType,
	ReportCategory,
	SeveredRelationshipType,
	SuggestionType,
	VisibilityLevel
)


T = TypeVar("T")
A = TypeVar("A")


def join_scope(value: Sequence[str] | str) -> str:
	if isinstance(value, str):
		return value

	return " ".join(value)


def split_scope(value: str | Sequence[str]) -> list[str]:
	if not isinstance(value, str):
		return list(value)

	return value.split(" ")


def url_parse(data: Any) -> Url:
	if not data:
		raise ValueError(f"Invalid url string: {data}")

	return Url.parse(data)


class ObjectBase(dict[str, Any]):
	"Base class for all API objects"

	FIELDS: dict[str, Any]
	"All of the fields associated with the class"


	def __init__(self, **kwargs: Any) -> None:
		"""
			Create a new object (usually from an API response).

			.. note:: ``ObjectBase`` can not be initiated by itself. Use a sub-object.

			:param kwargs: Key/value pairs to be assigned to the object
		"""

		if type(self) is ObjectBase:
			raise NotImplementedError()

		self._extra: dict[str, Any] = {}

		for key, value in kwargs.items():
			try:
				self[key] = value

			except InvalidFieldError:
				self._extra[key] = value


	def __getitem__(self, key: str) -> Any:
		if key not in self.FIELDS:
			raise KeyError(key)

		dict.get(self, key, None)


	def __setitem__(self, key: str, value: Any) -> None:
		if key not in self.FIELDS:
			raise InvalidFieldError(self, key)

		field = self.FIELDS[key]

		if value is None:
			self.pop(key, None)
			return

		if field.deserializer is not None:
			value = field.deserializer(value)

		dict.__setitem__(self, key, value)


	def __repr__(self) -> str:
		props = []

		for key in self.FIELDS:
			try:
				props.append(f"{key}={repr(self[key])}")

			except KeyError:
				continue

		return f"{type(self).__name__}({', '.join(props)})"


	@classmethod
	def parse(cls: type[Self], data: JsonBase | Mapping[str, Any] | str | bytes) -> Self:
		"""
			Parse a ``dict`` object or ``JSON`` string

			:param data: Data to parse
		"""

		data = JsonBase.parse(data)
		return cls(**data)


	def clear(self) -> None:
		dict.clear(self) # type: ignore[arg-type]
		self._extra.clear()


	def setdefault(self, key: str, value: Any = None) -> Any:
		try:
			return self[key]

		except KeyError:
			pass

		self[key] = value
		return value


	def to_dict(self) -> JsonBase:
		"Return the object as a JSON-safe ``dict`` object"

		data = JsonBase()

		for key, value in self.items():
			if value is None:
				data[key] = None
				continue

			if (field := self.FIELDS[key]).serializer is not None:
				data[key] = field.serializer(value)

			else:
				data[key] = value

		return data


	def to_json(self, indent: int | str | None = None) -> str:
		"Return the object as a JSON string"

		return self.to_dict().to_json(indent)


	def unassigned_values(self) -> dict[str, Any]:
		"Values not associated with a field"

		return deepcopy(self._extra)


	def update(self, data: dict[str, Any] | None, **kwargs: Any) -> None: # type: ignore[override]
		kwargs.update(data or {})

		for key, value in kwargs.items():
			self[key] = value


class Field(Generic[T]):
	def __init__(self,
				deserializer: Callable[[Any], T] | None = None,
				serializer: Callable[[T], Any] | None = None,
				key: str | None = None) -> None:
		"""
			Creates a new ``Field`` descriptor and adds itself to :attr:`ObjectBase.FIELDS`

			:param deserializer: Method to call when setting a value
			:param serializer: Method to call in :meth:`ObjectBase.to_dict` or
				:meth:`ObjectBase.to_json`
			:param key: Name of the key to use when getting or setting a value. This will be the
				name of the property by default.
		"""

		self.key: str = key or ""
		self.deserializer: Callable[[Any], T] | None = deserializer
		self.serializer: Callable[[T], Any] | None = serializer


	def __set_name__(self, cls: type[ObjectBase], key: str) -> None:
		if not self.key:
			self.key = key

		if not hasattr(cls, "FIELDS"):
			cls.FIELDS = {}

		cls.FIELDS[key] = self


	@overload
	def __get__(self, obj: ObjectBase, cls: Any) -> T:
		...


	@overload
	def __get__(self, obj: None, cls: Any) -> Self:
		...


	def __get__(self, obj: ObjectBase | None, cls: Any) -> Self | T:
		if obj is None:
			raise RuntimeError("Field is not a static property")

		try:
			return obj[self.key] # type: ignore[no-any-return]

		except KeyError:
			raise AttributeError(
				f"'{get_object_name(obj)}' does not have attribute '{self.key}'") from None


	def __set__(self, obj: ObjectBase, value: T) -> None:
		if self.deserializer is not None:
			value = self.deserializer(value)

		obj[self.key] = value


	def __delete__(self, obj: ObjectBase) -> None:
		del obj[self.key]


	@classmethod
	def list(cls: type[Self],
			deserializer: Callable[[Any], A] | type[A] | None,
			serializer: Callable[[A], Any] | type[A] | None,
			key: str | None = None) -> Self:
		"""
			Create a new list-based ``Field`` object

			:param deserializer: Method to call when setting a value
			:param serializer: Method to call in :meth:`ObjectBase.to_dict` or
				:meth:`ObjectBase.to_json`
			:param key: Name of the key to use when getting or setting a value. This will be the
				name of the property by default.
		"""

		return cls(deserializer, serializer, key) # type: ignore[arg-type]


class ListDeserializer(Generic[T]):
	def __init__(self, parser: Callable[[Any], T] | type[T] | None) -> None:
		self.parser: Callable[[Any], T] | type[T] | None = parser


	def __call__(self, data: list[Any]) -> list[T]:
		if self.parser is None:
			return data

		if type(self.parser) is type and issubclass(self.parser, (JsonBase, ObjectBase)):
			return [self.parser.parse(item) for item in data] # type: ignore[misc]

		return [self.parser(item) for item in data] # type: ignore[call-arg]


	def parse(self, data: list[Any]) -> list[T]:
		return self(data)


class ListSerializer(Generic[T]):
	def __init__(self, dumper: Callable[[T], Any] | type[T] | None) -> None:
		self.dumper: Callable[[T], Any] | type[T] | None = dumper


	def __call__(self, data: list[T]) -> list[Any]:
		if self.dumper is None:
			return data

		if type(self.dumper) is type and issubclass(self.dumper, (JsonBase, ObjectBase)):
			return [self.dumper.to_dict(item) for item in data] # type: ignore[arg-type,union-attr]

		return [self.dumper(item) for item in data] # type: ignore[call-arg]


## sub objects ##
class AccountField(ObjectBase):
	"`Account Field <https://docs.joinmastodon.org/entities/Account/#Field>`_"

	name: Field[str] = Field()
	value: Field[str] = Field()
	verified_at: Field[ApiDate | None] = Field(ApiDate.parse, str)


class AnnouncementAccount(ObjectBase):
	"`Announcement Account <https://docs.joinmastodon.org/entities/Announcement/#Account>`_"

	id: Field[str] = Field()
	username: Field[str] = Field()
	url: Field[Url] = Field(Url.parse)
	acct: Field[str] = Field()


class AnnouncementStatus(ObjectBase):
	"`Announcement Status <https://docs.joinmastodon.org/entities/Announcement/#Status>`_"

	id: Field[str] = Field()
	url: Field[Url] = Field(Url.parse)


class PreviewCard(ObjectBase):
	url: Field[Url] = Field(Url.parse)
	title: Field[str] = Field()
	description: Field[str] = Field()
	type: Field[PreviewCardType] = Field(PreviewCardType.parse)
	author_name: Field[str] = Field()
	authro_url: Field[Url] = Field(Url.parse)
	provider_name: Field[str] = Field()
	provider_url: Field[Url] = Field(Url.parse)
	html: Field[str] = Field()
	width: Field[int] = Field()
	height: Field[int] = Field()
	image: Field[Url] = Field(Url.parse)
	embed_url: Field[Url] = Field(Url.parse)
	blurhash: Field[str] = Field()


class CredentialRole(ObjectBase):
	id: Field[str] = Field()
	name: Field[str] = Field()
	color: Field[str] = Field()
	permissions: Field[PermissionFlag] = Field(PermissionFlag.parse)
	highlighted: Field[bool] = Field()


class CredentialSource(ObjectBase):
	note: Field[str] = Field()
	privacy: Field[str] = Field()
	sensitive: Field[bool] = Field()
	language: Field[str] = Field()
	follow_requests_count: Field[int] = Field()
	hide_collections: Field[bool] = Field()
	discoverable: Field[bool] = Field()
	indexable: Field[bool] = Field()

	fields: Field[list[AccountField]] = Field.list(AccountField, AccountField)


class Emoji(ObjectBase):
	name: Field[str] = Field(key = "shortcode")
	url: Field[Url] = Field(Url.parse)
	static_url: Field[Url] = Field(Url.parse)
	visible_in_picker: Field[bool] = Field()
	category: Field[str] = Field()


class FilterKeyword(ObjectBase):
	id: Field[str] = Field()
	keyword: Field[str] = Field()
	whole_word: Field[bool] = Field()


class FilterStatus(ObjectBase):
	id: Field[str] = Field()
	status_id: Field[str] = Field()


class Filter(ObjectBase):
	id: Field[str] = Field()
	title: Field[str] = Field()
	context: Field[list[str]] = Field()
	expires_at: Field[ApiDate] = Field(ApiDate.parse, str)
	filter_action: Field[FilterAction] = Field(FilterAction.parse)
	keywords: Field[list[FilterKeyword]] = Field.list(FilterKeyword, FilterKeyword)
	statuses: Field[list[FilterStatus]] = Field.list(FilterStatus, FilterStatus)


class FilterResult(ObjectBase):
	filter: Field[Filter] = Field(Filter.parse, Filter.to_dict)
	keyword_matches: Field[list[str]] = Field()
	status_matches: Field[list[str]] = Field()


class InstanceConfigAccounts(ObjectBase):
	max_featured_tags: Field[int] = Field()


class InstanceConfigMedia(ObjectBase):
	supported_mime_types: Field[list[str]] = Field()
	image_size_limit: Field[int] = Field()
	image_matrix_limit: Field[int] = Field()
	video_size_limit: Field[int] = Field()
	video_frame_rate_limit: Field[int] = Field()
	video_matrix_limit: Field[int] = Field()


class InstanceConfigPoll(ObjectBase):
	max_options: Field[int] = Field()
	max_characters_per_option: Field[int] = Field()
	min_expiration: Field[int] = Field()
	max_expiration: Field[int] = Field()


class InstanceConfigStatus(ObjectBase):
	max_characters: Field[int] = Field()
	characters_reserved_per_url: Field[int] = Field()
	supported_mime_types: Field[list[str]] = Field()


class InstanceConfigTranslation(ObjectBase):
	enabled: Field[bool] = Field()


class InstanceConfigUrls(ObjectBase):
	streaming: Field[Url] = Field(Url.parse)
	status: Field[str] = Field()


class InstanceConfigVapid(ObjectBase):
	public_key: Field[str] = Field()


class InstanceConfig(ObjectBase):
	urls: Field[InstanceConfigUrls] = Field(
		InstanceConfigUrls.parse, InstanceConfigUrls.to_dict
	)

	vapid: Field[InstanceConfigVapid] = Field(
		InstanceConfigVapid.parse, InstanceConfigVapid.to_dict
	)

	accounts: Field[InstanceConfigAccounts] = Field(
		InstanceConfigAccounts.parse, InstanceConfigAccounts.to_dict
	)

	statuses: Field[InstanceConfigStatus] = Field(
		InstanceConfigStatus.parse, InstanceConfigStatus.to_dict
	)

	media_attachments: Field[InstanceConfigMedia] = Field(
		InstanceConfigMedia.parse, InstanceConfigMedia.to_dict
	)

	translation: Field[InstanceConfigTranslation] = Field(
		InstanceConfigTranslation.parse, InstanceConfigTranslation.to_dict
	)

	polls: Field[InstanceConfigPoll] = Field(
		InstanceConfigPoll.parse, InstanceConfigPoll.to_dict
	)


class InstanceContact(ObjectBase):
	email: Field[str] = Field()
	account: Field[Account] = Field(lambda data: Account.parse(data), lambda data: data.to_dict())


class InstanceRegistration(ObjectBase):
	enabled: Field[bool] = Field()
	approval_required: Field[bool] = Field()
	message: Field[str] = Field()
	url: Field[Url] = Field(Url.parse)


class InstanceThumbnail(ObjectBase):
	url: Field[Url] = Field(Url.parse)


class InstanceUsageUsers(ObjectBase):
	active_month: Field[int] = Field()


class InstanceUsage(ObjectBase):
	users: Field[InstanceUsageUsers] = Field(InstanceUsageUsers.parse, InstanceUsageUsers.to_dict)


class Marker(ObjectBase):
	last_read_id: Field[str] = Field()
	version: Field[int] = Field()
	updated_at: Field[ApiDate] = Field(ApiDate.parse)


class Media(ObjectBase):
	id: Field[str] = Field()
	type: Field[MediaType] = Field(MediaType.parse)
	url: Field[Url] = Field(Url.parse)
	preview_url: Field[Url] = Field(Url.parse)
	remote_url: Field[Url] = Field(Url.parse)
	meta: Field[dict[str, Any]] = Field() # todo: figure out what keys this has
	description: Field[str] = Field()
	blurhash: Field[str] = Field()


class Mention(ObjectBase):
	id: Field[str] = Field()
	username: Field[str] = Field()
	url: Field[Url] = Field(Url.parse)
	acct: Field[str] = Field()


class NotificationPolicySummary(ObjectBase):
	pending_requests_count: Field[int] = Field()
	pending_notifications_count: Field[int] = Field()


class PollOption(ObjectBase):
	title: Field[str] = Field()
	votes_count: Field[int] = Field()


class Poll(ObjectBase):
	id: Field[str] = Field()
	expires_at: Field[ApiDate] = Field(ApiDate.parse, str)
	expired: Field[bool] = Field()
	multiple: Field[bool] = Field()
	votes_count: Field[int] = Field()
	voters_count: Field[int] = Field()
	voted: Field[bool] = Field()
	own_votes: Field[list[int]] = Field()
	emojis: Field[list[Emoji]] = Field.list(Emoji, Emoji)
	options: Field[list[PollOption]] = Field.list(PollOption, PollOption)


class Reaction(ObjectBase):
	name: Field[str] = Field()
	count: Field[int] = Field()
	me: Field[bool] = Field()
	url: Field[Url] = Field(url_parse)
	static_url: Field[Url] = Field(url_parse)


class RelationshipSeveranceEvent(ObjectBase):
	id: Field[str] = Field()
	type: Field[SeveredRelationshipType] = Field(SeveredRelationshipType.parse)
	purged: Field[bool] = Field()
	target_name: Field[str] = Field()
	relationship_count: Field[int] = Field()
	created_at: Field[ApiDate] = Field(ApiDate.parse)


class StatusApplication(ObjectBase):
	name: Field[str] = Field()
	website: Field[str] = Field()


class StatusTag(ObjectBase):
	name: Field[str] = Field()
	url: Field[Url] = Field(Url.parse)


class TagHistory(ObjectBase):
	day: Field[ApiDate] = Field(ApiDate.parse, ApiDate.timestamp)
	users: Field[int] = Field(int, str)
	accounts: Field[int] = Field(int, str)


class Tag(ObjectBase):
	name: Field[str] = Field()
	url: Field[str] = Field()
	following: Field[bool] = Field()
	history: Field[TagHistory]


class TranslationMedia(ObjectBase):
	id: Field[str] = Field()
	description: Field[str] = Field()


class TranslationPoll(ObjectBase):
	id: Field[str] = Field()
	options: Field[list[str]] = Field.list(lambda obj: obj["title"], lambda obj: {"title": obj})


## main objects ##
class AccessToken(ObjectBase):
	token_type: Field[str] = Field()
	access_token: Field[str] = Field()
	scope: Field[list[str]] = Field(split_scope, join_scope)
	created_at: Field[ApiDate] = Field(ApiDate.parse, str)


class Account(ObjectBase):
	id: Field[str] = Field()
	username: Field[str] = Field()
	acct: Field[str] = Field()
	display_name: Field[str] = Field()
	uri: Field[Url] = Field(Url.parse)
	url: Field[Url] = Field(Url.parse)
	note: Field[str] = Field()
	avatar: Field[Url] = Field(Url.parse)
	avatar_static: Field[Url] = Field(Url.parse)
	header: Field[Url] = Field(Url.parse)
	header_static: Field[Url] = Field(Url.parse)
	locked: Field[bool] = Field()
	bot: Field[bool] = Field()
	group: Field[bool] = Field()
	noindex: Field[bool] = Field()
	suspended: Field[bool] = Field()
	limited: Field[bool] = Field()
	discoverable: Field[bool] = Field()
	indexable: Field[bool] = Field()
	hide_collections: Field[bool] = Field()
	statuses_count: Field[int] = Field()
	followers_count: Field[int] = Field()
	following_count: Field[int] = Field()
	moved: Field[Account] = Field(lambda data: Account.parse(data), lambda data: data.to_dict())
	last_status_at: Field[ApiDate] = Field(ApiDate.parse, str)
	created_at: Field[ApiDate] = Field(ApiDate.parse, str)
	fields: Field[list[AccountField]] = Field.list(AccountField, AccountField)
	roles: Field[list[CredentialRole]] = Field.list(CredentialRole, CredentialRole)
	emojis: Field[list[Emoji]] = Field.list(Emoji, Emoji)

	# credential account only
	role: Field[CredentialRole] = Field(CredentialRole.parse, CredentialRole.to_dict)
	source: Field[CredentialSource] = Field(CredentialSource.parse, CredentialSource.to_dict)


class Activity(ObjectBase):
	week: Field[int] = Field(int, str)
	statuses: Field[int] = Field(int, str)
	logins: Field[int] = Field(int, str)
	registrations: Field[int] = Field(int, str)


class Announcement(ObjectBase):
	id: Field[str] = Field()
	content: Field[str] = Field()
	starts_at: Field[ApiDate] = Field(ApiDate.parse)
	ends_at: Field[ApiDate] = Field(ApiDate.parse)
	published: Field[bool] = Field()
	all_day: Field[bool] = Field()
	published_at: Field[ApiDate] = Field(ApiDate.parse)
	updated_at: Field[ApiDate] = Field(ApiDate.parse)
	read: Field[bool] = Field()
	emojis: Field[list[Emoji]] = Field.list(Emoji, Emoji)
	reactions: Field[list[Reaction]] = Field.list(Reaction, Reaction)

	mentions: Field[list[AnnouncementAccount]] = Field.list(
		AnnouncementAccount, AnnouncementAccount
	)

	statuses: Field[list[AnnouncementStatus]] = Field.list(
		AnnouncementStatus, AnnouncementStatus
	)

	tags: Field[list[StatusTag]] = Field.list(
		StatusTag, StatusTag
	)


class Application(ObjectBase):
	id: Field[str] = Field()
	name: Field[str] = Field()
	website: Field[Url] = Field(Url.parse)
	redirect_uri: Field[str] = Field()
	client_id: Field[str] = Field()
	client_secret: Field[str] = Field()
	scope: Field[list[str]] = Field(split_scope, join_scope)
	vapid_key: Field[str] = Field() # deprecated


class DomainBlock(ObjectBase):
	domain: Field[str] = Field()
	digest: Field[str] = Field()
	severity: Field[BlockSeverity] = Field(BlockSeverity.parse)
	comment: Field[str] = Field()


class ExtendedDescription(ObjectBase):
	content: Field[str] = Field()
	updated_at: Field[ApiDate] = Field(ApiDate.parse)


class FeaturedTag(ObjectBase):
	id: Field[str] = Field()
	name: Field[str] = Field()
	url: Field[Url] = Field(Url.parse)
	statuses_count: Field[int] = Field()
	last_status_at: Field[ApiDate] = Field(ApiDate.parse)


class Rule(ObjectBase):
	id: Field[str] = Field()
	text: Field[str] = Field()
	hint: Field[str] = Field()


class Instance(ObjectBase):
	domain: Field[str] = Field()
	title: Field[str] = Field()
	version: Field[str] = Field()
	source_url: Field[Url] = Field(Url.parse)
	description: Field[str] = Field()
	languages: Field[list[str]] = Field()
	usage: Field[InstanceUsage] = Field(InstanceUsage.parse, InstanceUsage.to_dict)
	thumbnail: Field[InstanceThumbnail] = Field(InstanceThumbnail.parse, InstanceThumbnail.to_dict)
	configuration: Field[InstanceConfig] = Field(InstanceConfig.parse, InstanceConfig.to_dict)
	contact: Field[InstanceContact] = Field(InstanceContact.parse, InstanceContact.to_dict)
	rules: Field[list[Rule]] = Field.list(Rule, Rule)

	registrations: Field[InstanceRegistration] = Field(
		InstanceRegistration.parse, InstanceRegistration.to_dict
	)


class LinkTrendHistory(ObjectBase):
	day: Field[ApiDate] = Field(lambda data: ApiDate.parse(int(data)))
	accounts: Field[int] = Field(int, str)
	users: Field[int] = Field(int, str)


class LinkTrend(ObjectBase):
	url: Field[Url] = Field(url_parse)
	title: Field[str] = Field()
	description: Field[str] = Field()
	type: Field[str] = Field()
	author_name: Field[str] = Field()
	author_url: Field[Url] = Field(url_parse)
	provider_name: Field[str] = Field()
	provider_url: Field[Url] = Field(url_parse)
	html: Field[Url] = Field()
	width: Field[int] = Field()
	height: Field[int] = Field()
	image: Field[Url] = Field(url_parse)
	embed_url: Field[Url] = Field(url_parse)
	blurhash: Field[Url] = Field()
	history: Field[list[LinkTrendHistory]] = Field.list(LinkTrendHistory, LinkTrendHistory)


class List(ObjectBase):
	id: Field[str] = Field()
	title: Field[str] = Field()
	replies_policy: Field[ListReplyPolicy] = Field(ListReplyPolicy.parse)


class Markers(ObjectBase):
	home: Field[Marker] = Field(Marker.parse, Marker.to_json)
	notifications: Field[Marker] = Field(Marker.parse, Marker.to_json)


class NotificationPolicy(ObjectBase):
	filter_not_following: Field[bool] = Field()
	filter_not_followers: Field[bool] = Field()
	filter_new_accounts: Field[bool] = Field()
	fitler_private_mentions: Field[bool] = Field()
	summary: Field[NotificationPolicySummary] = Field(
		NotificationPolicySummary.parse, NotificationPolicySummary.to_dict
	)


class OEmbed(ObjectBase):
	type: Field[str] = Field()
	version: Field[str] = Field()
	title: Field[str] = Field()
	author_name: Field[str] = Field()
	author_url: Field[Url] = Field(url_parse)
	provider_name: Field[str] = Field()
	provider_url: Field[Url] = Field(url_parse)
	cache_age: Field[str] = Field()
	html: Field[Url] = Field()
	width: Field[int] = Field()
	height: Field[int] = Field()


class Relationship(ObjectBase):
	id: Field[str] = Field()
	following: Field[bool] = Field()
	showing_reblogs: Field[bool] = Field()
	notifying: Field[bool] = Field()
	languages: Field[list[str]] = Field()
	followed_by: Field[bool] = Field()
	blocking: Field[bool] = Field()
	blocked_by: Field[bool] = Field()
	muting: Field[bool] = Field()
	muting_notifications: Field[bool] = Field()
	requested: Field[bool] = Field()
	requested_by: Field[bool] = Field()
	domain_blocking: Field[bool] = Field()
	endorsed: Field[bool] = Field()
	note: Field[str] = Field()


class Report(ObjectBase):
	id: Field[str] = Field()
	action_taken: Field[bool] = Field()
	action_taken_at: Field[ApiDate] = Field(ApiDate.parse)
	category: Field[ReportCategory] = Field(ReportCategory.parse)
	comment: Field[str] = Field()
	forwarded: Field[bool] = Field()
	created_at: Field[ApiDate] = Field(ApiDate.parse)
	status_ids: Field[list[str]] = Field()
	rule_ids: Field[list[str]] = Field()
	target_account: Field[str] = Field()


class ScheduledStatusParamsPoll(ObjectBase):
	options: Field[list[str]] = Field()
	expires_in: Field[int] = Field(int, str)
	multiple: Field[bool] = Field()
	hide_totals: Field[bool] = Field()


class ScheduledStatusParams(ObjectBase):
	text: Field[str] = Field()
	spoiler_text: Field[str] = Field()
	in_reply_to_id: Field[str] = Field()
	sensitive: Field[bool] = Field()
	language: Field[str] = Field()
	application_id: Field[int] = Field()
	media_ids: Field[list[str]] = Field()
	scheduled_at: Field[ApiDate] = Field(ApiDate.parse, ApiDate.to_string)
	idempotency: Field[str] = Field()
	with_rate_limit: Field[bool] = Field()

	poll: Field[ScheduledStatusParamsPoll] = Field(
		ScheduledStatusParamsPoll.parse, ScheduledStatusParamsPoll.to_dict
	)


class ScheduledStatus(ObjectBase):
	id: Field[str] = Field()
	scheduled_at: Field[ApiDate] = Field(ApiDate.parse, ApiDate.to_string)
	media_attachments: Field[list[Media]] = Field.list(Media, Media)

	params: Field[ScheduledStatusParams] = Field(
		ScheduledStatusParams.parse, ScheduledStatusParams.to_dict
	)


class Status(ObjectBase):
	id: Field[str] = Field()
	uri: Field[Url] = Field(Url.parse)
	url: Field[Url] = Field(Url.parse)
	created_at: Field[ApiDate] = Field(ApiDate.parse, str)
	account: Field[Account] = Field(Account.parse, Account.to_dict)
	content: Field[str] = Field()
	visibility: Field[VisibilityLevel] = Field(VisibilityLevel.parse)
	sensitive: Field[bool] = Field()
	spoiler_text: Field[str] = Field()
	application: Field[StatusApplication] = Field(StatusApplication.parse, StatusApplication.to_json)
	reblogs_count: Field[int] = Field()
	favourites_count: Field[int] = Field()
	replies_count: Field[int] = Field()
	in_reply_to_id: Field[str] = Field()
	in_reply_to_account_id: Field[str] = Field()
	language: Field[str] = Field()
	edited_at: Field[ApiDate] = Field(ApiDate.parse, str)
	favourited: Field[bool] = Field()
	reblogged: Field[bool] = Field()
	muted: Field[bool] = Field()
	bookmarked: Field[bool] = Field()
	pinned: Field[bool] = Field()
	local_only: Field[bool] = Field()
	reblog: Field[Status] = Field(lambda data: Status.parse(data), lambda data: data.to_dict())
	card: Field[PreviewCard] = Field(PreviewCard.parse, PreviewCard.to_dict)
	poll: Field[Poll] = Field(Poll.parse, Poll.to_dict)
	media_attachments: Field[list[Media]] = Field.list(Media, Media)
	mentions: Field[list[Mention]] = Field.list(Mention, Mention)
	tags: Field[list[Tag]] = Field.list(Tag, Tag)
	emojis: Field[list[Emoji]] = Field.list(Emoji, Emoji)
	filtered: Field[list[FilterResult]] = Field.list(FilterResult, FilterResult)


class Search(ObjectBase):
	accounts: Field[list[Account]] = Field.list(Account, Account)
	hashtags: Field[list[Tag]] = Field.list(Tag, Tag)
	statuses: Field[list[Status]] = Field.list(Status, Status)


class StatusContext(ObjectBase):
	ancestors: Field[list[Status]] = Field.list(Status, Status)
	descendants: Field[list[Status]] = Field.list(Status, Status)


class StatusSource(ObjectBase):
	id: Field[str] = Field()
	text: Field[str] = Field()
	spoiler_text: Field[str] = Field()


class StatusEdit(ObjectBase):
	content: Field[str] = Field()
	spoiler_text: Field[str] = Field()
	sensitive: Field[bool] = Field()
	created_at: Field[ApiDate] = Field(ApiDate.parse)
	account: Field[Account] = Field(Account.parse, Account.to_dict)
	poll: Field[Poll] = Field(Poll.parse, Poll.to_dict)
	emojis: Field[list[Emoji]] = Field.list(Emoji, Emoji)
	media_attachments: Field[list[Media]] = Field.list(Media, Media)


class Conversation(ObjectBase):
	id: Field[str] = Field()
	unread: Field[bool] = Field()
	last_status: Field[Status] = Field(Status.parse, Status.to_dict)
	accounts: Field[list[Account]] = Field.list(Account, Account)


class Suggestion(ObjectBase):
	source: SuggestionType
	account: Account


class Translation(ObjectBase):
	content: Field[str] = Field()
	spoiler_text: Field[str] = Field()
	poll: Field[TranslationPoll] = Field(TranslationPoll.parse, TranslationPoll.to_dict)
	detected_source_language: Field[str] = Field()
	provider: Field[str] = Field()
	media_attachments: Field[list[TranslationMedia]] = Field.list(
		TranslationMedia, TranslationMedia
	)


class WebPushSubscriptionAlerts(ObjectBase):
	follow: Field[bool] = Field()
	favourite: Field[bool] = Field()
	boost: Field[bool] = Field(key = "reblog")
	mention: Field[bool] = Field()
	poll: Field[bool] = Field()


class WebPushSubscription(ObjectBase):
	id: Field[str] = Field()
	endpoint: Field[Url] = Field()
	server_key: Field[str] = Field()
	alerts: Field[WebPushSubscriptionAlerts] = Field.list(
		WebPushSubscriptionAlerts, WebPushSubscriptionAlerts
	)


class Notification(ObjectBase):
	id: Field[str] = Field()
	type: Field[NotificationType] = Field(NotificationType.parse)
	created_at: Field[ApiDate] = Field(ApiDate.parse)
	account: Field[Account] = Field(Account.parse, Account.to_dict)
	status: Field[Status] = Field(Status.parse, Status.to_dict)
	report: Field[Report] = Field(Report.parse, Report.to_dict)
	relationship_severance_event: Field[RelationshipSeveranceEvent] = Field(
		RelationshipSeveranceEvent.parse, RelationshipSeveranceEvent.to_dict
	)


class NotificationRequest(ObjectBase):
	id: Field[str] = Field()
	created_at: Field[ApiDate] = Field(ApiDate.parse)
	updated_at: Field[ApiDate] = Field(ApiDate.parse)
	from_account: Field[Account] = Field(Account.parse, Account.to_dict)
	notifications_count: Field[int] = Field()
	last_status: Field[Status] = Field(Status.parse, Status.to_dict)
