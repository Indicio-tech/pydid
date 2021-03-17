"""DID Doc Service."""

from voluptuous import ALLOW_EXTRA, All, Schema, Url

from ..did_url import DIDUrl


class Service:
    """Representation of DID Document Services."""

    validate = Schema(
        {"id": All(str, DIDUrl.validate), "type": str, "serviceEndpoint": Url()},
        extra=ALLOW_EXTRA,
        required=True,
    )

    def __init__(self, id_: DIDUrl, type_: str, endpoint: str, **extra):
        """Initialize Service."""
        self._id = id_
        self._type = type_
        self._endpoint = endpoint
        self._extra = extra

    @property
    def id(self):
        """Return id."""
        return self._id

    @property
    def type(self):
        """Return type."""
        return self._type

    @property
    def endpoint(self):
        """Return endpoint."""
        return self._endpoint

    @property
    def extra(self):
        """Return extra."""
        return self._extra

    def serialize(self):
        """Return serialized representation of Service."""
        return {
            "id": self.id,
            "type": self.type,
            "serviceEndpoint": self.endpoint,
            **self.extra,
        }

    @classmethod
    def deserialize(cls, value: dict):
        """Deserialize into Service."""
        value = cls.validate(value)
        required = ("id", "type", "serviceEndpoint")
        extra = {
            key: extra_value
            for key, extra_value in value.items()
            if key not in required
        }
        return cls(*[value[key] for key in required], **extra)
