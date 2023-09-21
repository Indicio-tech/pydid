"""Test Service."""

from typing import Union
from pydantic import parse_obj_as
import pytest

from pydid import Service, DIDCommService
from pydid.service import DIDCommV1Service, DIDCommV2Service

SERVICES = [
    {
        "id": "did:example:123#linked-domain",
        "type": "LinkedDomains",
        "serviceEndpoint": "https://bar.example.com",
    },
    {
        "id": "did:example:123#did-communication",
        "type": "did-communication",
        "serviceEndpoint": "https://agents-r-us.com",
        "recipientKeys": ["did:example:123#keys-1"],
        "routingKeys": [
            "did:key:z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH"
            "#z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH"
        ],
    },
    {
        "id": "did:example:123#linked-domain",
        "type": "LinkedDomains",
        "serviceEndpoint": "",
    },
    {
        "id": "did:example:123#didcomm-1",
        "type": "DIDCommMessaging",
        "serviceEndpoint": "https://example.com/endpoint1",
        "routingKeys": ["did:example:somemediator#somekey1"],
        "accept": ["didcomm/v2", "didcomm/aip2;env=rfc587"],
    },
    {
        "id": "did:example:123#didcomm-1",
        "type": "did-communication",
        "serviceEndpoint": "didcomm:transport/queue",
        "recipientKeys": ["did:example:123#keys-1"],
        "routingKeys": [],
        "accept": ["didcomm/aip2;env=rfc587"],
    },
    {
        "id": "did:example:123456789abcdefghi#didcomm-1",
        "type": "DIDCommMessaging",
        "serviceEndpoint": [
            {
                "uri": "https://example.com/path",
                "accept": ["didcomm/v2", "didcomm/aip2;env=rfc587"],
                "routingKeys": ["did:example:somemediator#somekey"],
            }
        ],
    },
]

INVALID_SERVICES = [
    {"type": "xdi", "serviceEndpoint": "https://example.com"},
    {
        "id": "did:example:123#linked-domain",
        "serviceEndpoint": "https://bar.example.com",
    },
    {
        "id": "did:example:123",
        "type": "LinkedDomains",
        "serviceEndpoint": "https://bar.example.com",
    },
    {
        "id": "did:example:123#linked-domain",
        "type": "LinkedDomains",
        "serviceEndpoint": True,
    },
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


DIDCOMM_SERVICES = [
    {
        "id": "did:example:123#did-communication",
        "type": "did-communication",
        "serviceEndpoint": "https://agents-r-us.com",
        "recipientKeys": ["did:example:123#keys-1"],
        "routingKeys": [
            "did:key:z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH"
            "#z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH"
        ],
        "priority": 0,
    },
    {
        "id": "did:example:123#did-communication",
        "type": "did-communication",
        "serviceEndpoint": "https://agents-r-us.com",
        "recipientKeys": ["did:example:123#keys-1"],
        "routingKeys": [],
        "priority": 0,
    },
    {
        "id": "did:example:123#indy-agent",
        "type": "IndyAgent",
        "serviceEndpoint": "https://agents-r-us.com",
        "recipientKeys": ["did:example:123#keys-1"],
        "routingKeys": [],
        "priority": 0,
        "accept": ["didcomm/aip2;env=rfc19"],
    },
    {
        "id": "did:example:123#didcomm-1",
        "type": "DIDCommMessaging",
        "serviceEndpoint": "https://example.com/endpoint1",
        "recipientKeys": ["did:example:123#keys-1"],
        "routingKeys": ["did:example:somemediator#somekey1"],
        "priority": 0,
        "accept": ["didcomm/v2", "didcomm/aip2;env=rfc587"],
    },
    {
        "id": "did:example:123#didcomm-1",
        "type": "did-communication",
        "serviceEndpoint": "didcomm:transport/queue",
        "recipientKeys": ["did:example:123#keys-1"],
        "routingKeys": [],
        "priority": 0,
        "accept": ["didcomm/aip2;env=rfc587"],
    },
    {
        "id": "did:example:123456789abcdefghi#didcomm-1",
        "type": "DIDCommMessaging",
        "serviceEndpoint": [
            {
                "uri": "https://example.com/path",
                "accept": ["didcomm/v2", "didcomm/aip2;env=rfc587"],
                "routingKeys": ["did:example:somemediator#somekey"],
            }
        ],
    },
    {
        "id": "did:example:123456789abcdefghi#didcomm-1",
        "type": "DIDCommMessaging",
        "serviceEndpoint": [
            {
                "uri": "didcomm:transport/queue",
                "accept": ["didcomm/v2"],
                "routingKeys": [],
            }
        ],
    },
    {
        "id": "did:example:123456789abcdefghi#didcomm-1",
        "type": "DIDCommMessaging",
        "serviceEndpoint": [
            {
                "uri": "did:example:mediator",
                "accept": ["didcomm/v2"],
                "routingKeys": [],
            }
        ],
    },
]

DIDCOMM_INVALID_SERVICES = [
    *INVALID_SERVICES,
    {
        "id": "did:example:123#linked-domain",
        "type": "LinkedDomains",
        "serviceEndpoint": "https://bar.example.com",
    },
    {
        "id": "did:example:123#did-communication",
        "type": "did-communication",
        "serviceEndpoint": "https://agents-r-us.com",
        "recipientKeys": ["did:example:123#keys-1"],
        "routingKeys": [],
        "extra key": "that should fail",
    },
]


@pytest.mark.parametrize("service", DIDCOMM_SERVICES)
def test_didcomm_validate(service):
    parse_obj_as(Union[DIDCommV1Service, DIDCommV2Service], service)


@pytest.mark.parametrize("service", DIDCOMM_INVALID_SERVICES)
def test_didcomm_fails_invalid(service):
    with pytest.raises(ValueError):
        parse_obj_as(Union[DIDCommV1Service, DIDCommV2Service], service)


@pytest.mark.parametrize("service_raw", DIDCOMM_SERVICES)
def test_didcomm_serialization(service_raw):
    service = parse_obj_as(Union[DIDCommV1Service, DIDCommV2Service], service_raw)
    assert service.serialize() == service_raw


def test_use_endpoint():
    service = Service.deserialize(SERVICES[0])
    assert service.service_endpoint == "https://bar.example.com"
    assert "https" in service.service_endpoint
