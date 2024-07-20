import typing

from pydantic import Field

from ._base import BaseModel


class Recipient(BaseModel):
    """Represents a recipient in MagicBell."""

    email: typing.Optional[str] = Field(None, description="The user's email")
    external_id: typing.Optional[str] = Field(
        description="A unique string that MagicBell can utilize to uniquely identify the user. "
        "We recommend setting this attribute to the ID of the user in your database. "
        "Provide the external id if the user's email is unavailable.",
        default=None,
    )
    matches: typing.Optional[str] = Field(
        description="An SQL-like expression to match users by their stored attributes. "
        'Set it to "*" to send a notification to all users.',
        default=None,
    )


class ChannelOverrides(BaseModel):
    title: typing.Optional[str] = Field(None, description="Overridden title for this channel")
    content: typing.Optional[str] = Field(None, description="Overridden content for this channel")
    action_url: typing.Optional[str] = Field(
        None, description="Overridden action URL for this channel"
    )


class NotificationChannelsOverrides(BaseModel):
    in_app: typing.Optional[ChannelOverrides] = None
    email: typing.Optional[ChannelOverrides] = None
    web_push: typing.Optional[ChannelOverrides] = None
    mobile_push: typing.Optional[ChannelOverrides] = None


class NotificationProvidersOverrides(BaseModel):
    sendgrid: typing.Optional[typing.Dict[typing.Any, typing.Any]] = Field(
        description="Set of key-value pairs that you can pass on to Sendgrid. "
        "Applied only if it is configured for your project.",
        default=None,
    )
    mailgun: typing.Optional[typing.Dict[typing.Any, typing.Any]] = Field(
        description="Set of key-value pairs that you can pass on to Mailgun. "
        "Applied only if it is configured for your project.",
        default=None,
    )
    postmark: typing.Optional[typing.Dict[typing.Any, typing.Any]] = Field(
        description="Set of key-value pairs that you can pass on to Postmark. "
        "Applied only if it is configured for your project.",
        default=None,
    )
    ios: typing.Optional[typing.Dict[typing.Any, typing.Any]] = Field(
        description="Set of key-value pairs that you can pass on to APNS. "
        "Applied only if it is configured for your project.",
        default=None,
    )
    android: typing.Optional[typing.Dict[typing.Any, typing.Any]] = Field(
        description="Set of key-value pairs that you can pass on to FCM. "
        "Applied only if it is configured for your project.",
        default=None,
    )


class NotificationOverrides(BaseModel):
    channels: typing.Optional[NotificationChannelsOverrides] = Field(
        description="Overrides for specific channels", default=None
    )
    providers: typing.Optional[NotificationProvidersOverrides] = Field(
        description="Overrides for specific providers (Sendgrid, Postmark, APNs, etc)", default=None
    )


class Notification(BaseModel):
    title: str = Field(description="Title of the notification.")
    category: typing.Optional[str] = Field(
        description="Category the notification belongs to. "
        "This is useful to allow users to set their preferences.",
        default=None,
    )
    content: typing.Optional[str] = Field(
        description="Content of the notification. "
        "If you provide HTML content, the notification inbox will render it correctly.",
        default=None,
    )
    action_url: typing.Optional[str] = Field(
        description="A URL to redirect the user to when they click the notification in their notification inbox.",  # noqa: E501
        default=None,
    )
    custom_attributes: typing.Optional[typing.Dict[str, typing.Any]] = Field(
        description="Set of key-value pairs that you can attach to a notification. "
        "It accepts objects for the value of a key. "
        "You can use it to share data between channels or to render a custom UI.",
        default=None,
    )
    topic: typing.Optional[str] = Field(
        description="Topic the notification belongs to. This is useful to create threads.",
        default=None,
    )
    recipients: typing.List[Recipient] = Field(
        min_length=1,
        max_length=1000,
        description="Users to send the notification to. "
        "You can specify up to 1000 users at once. Use matches to send a notification to everyone",
    )
    overrides: typing.Optional[NotificationOverrides] = Field(
        description="Optional overrides to configure notifications per target destination",
        default=None,
    )


class WrappedNotification(BaseModel):
    broadcast: Notification


class CreatedNotificationBroadcast(BaseModel):
    id: str


class WrappedCreatedNotificationBroadcast(BaseModel):
    broadcast: CreatedNotificationBroadcast
