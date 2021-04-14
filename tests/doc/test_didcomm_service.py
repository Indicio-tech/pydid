"""Test DIDComm Service."""

import pytest

from pydid.doc.service import DIDCommService

from .test_service import INVALID_SERVICES as BASE_INVALID_SERVICES

SERVICE0 = {
    "id": "did:example:123#did-communication",
    "type": "did-communication",
    "serviceEndpoint": "https://agents-r-us.com",
    "recipientKeys": ["did:example:123#keys-1"],
    "routingKeys": [
        "did:key:z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH"
        "#z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH"
    ],
    "priority": 0,
}

SERVICE1 = {
    "id": "did:example:123#did-communication",
    "type": "did-communication",
    "serviceEndpoint": "https://agents-r-us.com",
    "recipientKeys": ["did:example:123#keys-1"],
    "routingKeys": [],
    "priority": 0,
}

SERVICE2 = {
    "id": "did:example:123#indy-agent",
    "type": "IndyAgent",
    "serviceEndpoint": "https://agents-r-us.com",
    "recipientKeys": ["did:example:123#keys-1"],
    "routingKeys": [],
    "priority": 0,
}

SERVICES = [SERVICE0, SERVICE1, SERVICE2]

INVALID_SERVICE0 = {
    "id": "did:example:123#linked-domain",
    "type": "LinkedDomains",
    "serviceEndpoint": "https://bar.example.com",
}

INVALID_SERVICE1 = {
    "id": "did:example:123#did-communication",
    "type": "did-communication",
    "serviceEndpoint": "https://agents-r-us.com",
    "recipientKeys": ["did:example:123#keys-1"],
    "routingKeys": [],
    "extra key": "that should fail",
}

INVALID_SERVICES = [*BASE_INVALID_SERVICES, INVALID_SERVICE0, INVALID_SERVICE1]


@pytest.mark.parametrize("service", SERVICES)
def test_validate(service):
    DIDCommService.validate(service)


@pytest.mark.parametrize("service", INVALID_SERVICES)
def test_fails_invalid(service):
    with pytest.raises(ValueError):
        DIDCommService.validate(service)


@pytest.mark.parametrize("service_raw", SERVICES)
def test_serialization(service_raw):
    service = DIDCommService.deserialize(service_raw)
    assert service.serialize() == service_raw
