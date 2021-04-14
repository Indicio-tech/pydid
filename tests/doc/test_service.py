"""Test Service."""

import pytest

from pydid.doc.service import Service

SERVICE0 = {
    "id": "did:example:123#linked-domain",
    "type": "LinkedDomains",
    "serviceEndpoint": "https://bar.example.com",
}
SERVICE1 = {
    "id": "did:example:123#did-communication",
    "type": "did-communication",
    "serviceEndpoint": "https://agents-r-us.com",
    "recipientKeys": ["did:example:123#keys-1"],
    "routingKeys": [
        "did:key:z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH"
        "#z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH"
    ],
}
SERVICE2 = {
    "id": "did:example:123#linked-domain",
    "type": "LinkedDomains",
    "serviceEndpoint": "",
}

SERVICES = [SERVICE0, SERVICE1, SERVICE2]

INVALID_SERVICE0 = {"type": "xdi", "serviceEndpoint": "https://example.com"}

INVALID_SERVICE1 = {
    "id": "did:example:123#linked-domain",
    "serviceEndpoint": "https://bar.example.com",
}

INVALID_SERVICE2 = {
    "id": "did:example:123",
    "type": "LinkedDomains",
    "serviceEndpoint": "https://bar.example.com",
}

INVALID_SERVICE3 = {
    "id": "did:example:123#linked-domain",
    "type": "LinkedDomains",
    "serviceEndpoint": "not a url",
}

INVALID_SERVICES = [
    INVALID_SERVICE0,
    INVALID_SERVICE1,
    INVALID_SERVICE2,
    INVALID_SERVICE3,
]


@pytest.mark.parametrize("service", SERVICES)
def test_validates_valid(service):
    Service.validate(service)


@pytest.mark.parametrize("service", INVALID_SERVICES)
def test_fails_invalid(service):
    with pytest.raises(ValueError):
        Service.validate(service)


@pytest.mark.parametrize("service_raw", SERVICES)
def test_serialization(service_raw):
    service = Service.deserialize(service_raw)
    assert service.serialize() == service_raw
