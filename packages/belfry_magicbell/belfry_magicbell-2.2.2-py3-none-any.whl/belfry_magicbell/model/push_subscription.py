import typing

from pydantic import Field

from ._base import BaseModel


class PushSubscription(BaseModel):
    id: typing.Optional[str] = Field(
        description="The push subscription's MagicBell ID (readonly).", default=None
    )
    device_token: str = Field(
        description="Token that identifies the device. This is usually generated automatically by your app once installed."
    )
    platform: str = Field(
        description="The platform where the device token was generated from. This value is used to determine the delivery mechanism for mobile push notifications. Either 'ios', 'android' or 'safari'."
    )
    app_bundle_id: typing.Optional[str] = Field(
        description="The bundle ID of your app. This value is used to determine the delivery mechanism for mobile push notifications based on your workflow so that you can link several mobile applications to one project.",
        default=None,
    )


class WrappedPushSubscription(BaseModel):
    push_subscription: PushSubscription
