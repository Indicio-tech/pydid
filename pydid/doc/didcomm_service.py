"""Service type for DID Communication Services."""

from typing import List

from voluptuous import PREVENT_EXTRA, All, Any, Schema, Coerce

from ..did_url import DIDUrl
from ..validation import wrap_validation_error, Into
from .service import Service, ServiceValidationError


class DIDCommService(Service):
    """DID Communication Service."""

    _validator = Service._validator.extend(
        {
            "type": Any("IndyAgent", "did-communication"),
            "recipientKeys": [All(str, DIDUrl.validate)],
            "routingKeys": [All(str, DIDUrl.validate)],
        },
        extra=PREVENT_EXTRA,
    )

    def __init__(
        self,
        id_: DIDUrl,
        endpoint: str,
        recipient_keys: List[DIDUrl],
        *,
        type_: str = None,
        routing_keys: List[DIDUrl] = None
    ):
        """Initialize DIDCommService."""
        super().__init__(id_, type_ or "did-communication", endpoint)
        self._recipient_keys = recipient_keys
        self._routing_keys = routing_keys or []

    @property
    def recipient_keys(self):
        """Return recipient_keys."""
        return self._recipient_keys

    @property
    def routing_keys(self):
        """Return routing_keys."""
        return self._routing_keys

    def serialize(self):
        """Return serialized representation of DIDCommService."""
        did_urls = Schema([Coerce(str)])
        return {
            "id": str(self.id),
            "type": self.type,
            "serviceEndpoint": self.endpoint,
            "recipientKeys": did_urls(self.recipient_keys),
            "routingKeys": did_urls(self.routing_keys),
        }

    @classmethod
    @wrap_validation_error(
        ServiceValidationError, message="Failed to validate DIDComm service"
    )
    def validate(cls, value: dict):
        """Validate value against DIDCommService."""
        return cls._validator(value)

    @classmethod
    @wrap_validation_error(
        ServiceValidationError, message="Failed to deserialize DIDComm service"
    )
    def deserialize(cls, value: dict):
        """Deserialize into Service."""
        value = cls.validate(value)
        deserializer = Schema(
            {
                Into("id", "id_"): DIDUrl.parse,
                Into("type", "type_"): str,
                Into("serviceEndpoint", "endpoint"): str,
                Into("recipientKeys", "recipient_keys"): [DIDUrl.parse],
                Into("routingKeys", "routing_keys"): [DIDUrl.parse],
            }
        )
        value = deserializer(value)
        return cls(**value)
