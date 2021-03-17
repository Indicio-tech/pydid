"""Service type for DID Communication Services."""

from typing import List

from voluptuous import PREVENT_EXTRA, All, Any

from ..did_url import DIDUrl
from .service import Service


class DIDCommService(Service):
    """DID Communication Service."""

    validate = Service.validate.extend(
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
        type_: str = "did-communication",
        routing_keys: List[DIDUrl] = None
    ):
        """Initialize DIDCommService."""
        super().__init__(id_, type_, endpoint)
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
        return {
            "id": self.id,
            "type": self.type,
            "serviceEndpoint": self.endpoint,
            "recipientKeys": self.recipient_keys,
            "routingKeys": self.routing_keys,
        }

    @classmethod
    def deserialize(cls, value: dict):
        """Deserialize into Service."""
        value = cls.validate(value)
        return cls(
            id_=value["id"],
            type_=value["type"],
            endpoint=value["serviceEndpoint"],
            recipient_keys=value["recipientKeys"],
            routing_keys=value["routingKeys"],
        )
