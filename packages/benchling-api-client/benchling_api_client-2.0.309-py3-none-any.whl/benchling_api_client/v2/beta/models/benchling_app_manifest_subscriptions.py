from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError, UnknownType
from ..models.delivery_method import DeliveryMethod
from ..models.event_created_message_subscription_v0_beta import EventCreatedMessageSubscriptionV0Beta
from ..models.message_subscription_webhook_v2_beta import MessageSubscriptionWebhookV2Beta
from ..types import UNSET, Unset

T = TypeVar("T", bound="BenchlingAppManifestSubscriptions")


@attr.s(auto_attribs=True, repr=False)
class BenchlingAppManifestSubscriptions:
    """Subscriptions allow an app to receive notifications when certain actions and changes occur in Benchling."""

    _delivery_method: DeliveryMethod
    _messages: List[
        Union[EventCreatedMessageSubscriptionV0Beta, MessageSubscriptionWebhookV2Beta, UnknownType]
    ]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("delivery_method={}".format(repr(self._delivery_method)))
        fields.append("messages={}".format(repr(self._messages)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BenchlingAppManifestSubscriptions({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        delivery_method = self._delivery_method.value

        messages = []
        for messages_item_data in self._messages:
            if isinstance(messages_item_data, UnknownType):
                messages_item = messages_item_data.value
            elif isinstance(messages_item_data, EventCreatedMessageSubscriptionV0Beta):
                messages_item = messages_item_data.to_dict()

            else:
                messages_item = messages_item_data.to_dict()

            messages.append(messages_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if delivery_method is not UNSET:
            field_dict["deliveryMethod"] = delivery_method
        if messages is not UNSET:
            field_dict["messages"] = messages

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_delivery_method() -> DeliveryMethod:
            _delivery_method = d.pop("deliveryMethod")
            try:
                delivery_method = DeliveryMethod(_delivery_method)
            except ValueError:
                delivery_method = DeliveryMethod.of_unknown(_delivery_method)

            return delivery_method

        try:
            delivery_method = get_delivery_method()
        except KeyError:
            if strict:
                raise
            delivery_method = cast(DeliveryMethod, UNSET)

        def get_messages() -> List[
            Union[EventCreatedMessageSubscriptionV0Beta, MessageSubscriptionWebhookV2Beta, UnknownType]
        ]:
            messages = []
            _messages = d.pop("messages")
            for messages_item_data in _messages:

                def _parse_messages_item(
                    data: Union[Dict[str, Any]]
                ) -> Union[
                    EventCreatedMessageSubscriptionV0Beta, MessageSubscriptionWebhookV2Beta, UnknownType
                ]:
                    messages_item: Union[
                        EventCreatedMessageSubscriptionV0Beta, MessageSubscriptionWebhookV2Beta, UnknownType
                    ]
                    discriminator_value: str = cast(str, data.get("type"))
                    if discriminator_value is not None:
                        if discriminator_value == "v0-beta.event.created":
                            messages_item = EventCreatedMessageSubscriptionV0Beta.from_dict(
                                data, strict=False
                            )

                            return messages_item
                        if discriminator_value == "v0-beta.lifecycle.activateRequested":
                            messages_item = MessageSubscriptionWebhookV2Beta.from_dict(data, strict=False)

                            return messages_item
                        if discriminator_value == "v0-beta.lifecycle.deactivated":
                            messages_item = MessageSubscriptionWebhookV2Beta.from_dict(data, strict=False)

                            return messages_item
                        if discriminator_value == "v2-beta.app.configuration.updated":
                            messages_item = MessageSubscriptionWebhookV2Beta.from_dict(data, strict=False)

                            return messages_item
                        if discriminator_value == "v2-beta.assayRun.created":
                            messages_item = MessageSubscriptionWebhookV2Beta.from_dict(data, strict=False)

                            return messages_item
                        if discriminator_value == "v2-beta.assayRun.updated.fields":
                            messages_item = MessageSubscriptionWebhookV2Beta.from_dict(data, strict=False)

                            return messages_item
                        if discriminator_value == "v2-beta.entity.registered":
                            messages_item = MessageSubscriptionWebhookV2Beta.from_dict(data, strict=False)

                            return messages_item
                        if discriminator_value == "v2-beta.entry.created":
                            messages_item = MessageSubscriptionWebhookV2Beta.from_dict(data, strict=False)

                            return messages_item
                        if discriminator_value == "v2-beta.entry.updated.fields":
                            messages_item = MessageSubscriptionWebhookV2Beta.from_dict(data, strict=False)

                            return messages_item
                        if discriminator_value == "v2-beta.entry.updated.reviewRecord":
                            messages_item = MessageSubscriptionWebhookV2Beta.from_dict(data, strict=False)

                            return messages_item
                        if discriminator_value == "v2-beta.request.created":
                            messages_item = MessageSubscriptionWebhookV2Beta.from_dict(data, strict=False)

                            return messages_item
                        if discriminator_value == "v2-beta.request.updated.fields":
                            messages_item = MessageSubscriptionWebhookV2Beta.from_dict(data, strict=False)

                            return messages_item
                        if discriminator_value == "v2-beta.request.updated.status":
                            messages_item = MessageSubscriptionWebhookV2Beta.from_dict(data, strict=False)

                            return messages_item
                        if discriminator_value == "v2-beta.workflowOutput.created":
                            messages_item = MessageSubscriptionWebhookV2Beta.from_dict(data, strict=False)

                            return messages_item
                        if discriminator_value == "v2-beta.workflowOutput.updated.fields":
                            messages_item = MessageSubscriptionWebhookV2Beta.from_dict(data, strict=False)

                            return messages_item
                        if discriminator_value == "v2-beta.workflowTask.created":
                            messages_item = MessageSubscriptionWebhookV2Beta.from_dict(data, strict=False)

                            return messages_item
                        if discriminator_value == "v2-beta.workflowTask.updated.assignee":
                            messages_item = MessageSubscriptionWebhookV2Beta.from_dict(data, strict=False)

                            return messages_item
                        if discriminator_value == "v2-beta.workflowTask.updated.fields":
                            messages_item = MessageSubscriptionWebhookV2Beta.from_dict(data, strict=False)

                            return messages_item
                        if discriminator_value == "v2-beta.workflowTask.updated.scheduledOn":
                            messages_item = MessageSubscriptionWebhookV2Beta.from_dict(data, strict=False)

                            return messages_item
                        if discriminator_value == "v2-beta.workflowTask.updated.status":
                            messages_item = MessageSubscriptionWebhookV2Beta.from_dict(data, strict=False)

                            return messages_item
                        if discriminator_value == "v2-beta.workflowTaskGroup.created":
                            messages_item = MessageSubscriptionWebhookV2Beta.from_dict(data, strict=False)

                            return messages_item
                        if discriminator_value == "v2-beta.workflowTaskGroup.updated.watchers":
                            messages_item = MessageSubscriptionWebhookV2Beta.from_dict(data, strict=False)

                            return messages_item

                        return UnknownType(value=data)
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        messages_item = EventCreatedMessageSubscriptionV0Beta.from_dict(data, strict=True)

                        return messages_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        messages_item = MessageSubscriptionWebhookV2Beta.from_dict(data, strict=True)

                        return messages_item
                    except:  # noqa: E722
                        pass
                    return UnknownType(data)

                messages_item = _parse_messages_item(messages_item_data)

                messages.append(messages_item)

            return messages

        try:
            messages = get_messages()
        except KeyError:
            if strict:
                raise
            messages = cast(
                List[
                    Union[
                        EventCreatedMessageSubscriptionV0Beta, MessageSubscriptionWebhookV2Beta, UnknownType
                    ]
                ],
                UNSET,
            )

        benchling_app_manifest_subscriptions = cls(
            delivery_method=delivery_method,
            messages=messages,
        )

        benchling_app_manifest_subscriptions.additional_properties = d
        return benchling_app_manifest_subscriptions

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def delivery_method(self) -> DeliveryMethod:
        """The delivery method for the subscriptions. Currently only webhook is supported."""
        if isinstance(self._delivery_method, Unset):
            raise NotPresentError(self, "delivery_method")
        return self._delivery_method

    @delivery_method.setter
    def delivery_method(self, value: DeliveryMethod) -> None:
        self._delivery_method = value

    @property
    def messages(
        self,
    ) -> List[Union[EventCreatedMessageSubscriptionV0Beta, MessageSubscriptionWebhookV2Beta, UnknownType]]:
        if isinstance(self._messages, Unset):
            raise NotPresentError(self, "messages")
        return self._messages

    @messages.setter
    def messages(
        self,
        value: List[
            Union[EventCreatedMessageSubscriptionV0Beta, MessageSubscriptionWebhookV2Beta, UnknownType]
        ],
    ) -> None:
        self._messages = value
