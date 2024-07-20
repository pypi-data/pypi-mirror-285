import typing

from ..model.push_subscription import WrappedPushSubscription
from ..model.response import Response
from ._base import BaseAPI
from ._parsing import build_request_content, build_response


class PushSubscriptionAPI(BaseAPI):
    async def create_push_subscription(
        self,
        external_id: str,
        wrapped_push_subscription: typing.Union[WrappedPushSubscription, typing.Dict],
    ) -> WrappedPushSubscription:
        """
        Register a device token for push notifications.

        Ref: https://www.magicbell.com/docs/rest-api/reference#push-subscriptions-create
        """
        response = await self.client.post(
            "/push_subscriptions",
            headers=self.configuration.get_user_external_id_headers(external_id=external_id),
            content=build_request_content(wrapped_push_subscription),
        )
        return build_response(response=response, out_type=WrappedPushSubscription).parsed

    async def delete_push_subscription(
        self, external_id: str, device_token: str
    ) -> Response[typing.Type[None]]:
        """
        Deletes the registered device token to remove the mobile push subscription.

        Ref: https://www.magicbell.com/docs/rest-api/reference#push-subscriptions-delete
        """
        url = f"/push_subscriptions/{device_token}"
        response = await self.client.delete(
            url, headers=self.configuration.get_user_external_id_headers(external_id=external_id)
        )
        return build_response(response=response, out_type=None)
