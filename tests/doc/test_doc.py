"""Test DIDDocument object."""

from collections import namedtuple
import copy

import pytest
from typing_extensions import Annotated, Literal

from pydid.did_url import DIDUrl, InvalidDIDUrlError
from pydid.doc.builder import DIDDocumentBuilder
from pydid.doc.doc import (
    DIDDocument,
    DIDDocumentError,
    DIDDocumentRoot,
    IDNotFoundError,
    NonconformantDocument,
)
from pydid.service import DIDCommV2Service, Service
from pydid.service import DIDCommService
from pydid.verification_method import (
    Ed25519VerificationKey2018,
    VerificationMaterial,
    VerificationMethod,
)

VerificationSuite = namedtuple(
    "VerificationSuite", ["type", "verification_material_prop"]
)


class ExampleVerificationMethod(VerificationMethod):
    type: Literal["Example"]
    public_key_example: Annotated[str, VerificationMaterial]


DOC0 = {
    "@context": ["https://w3id.org/did/v0.11"],
    "id": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
    "authentication": [
        {
            "id": "did:example:123#authentication-1",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
            "publicKeyBase58": "8NNydiyd3KjF46ERwY7rycTBvGKRh4J1BbnYvTYCK283",
        }
    ],
    "capabilityInvocation": [
        {
            "id": "did:example:123#capability-invocation-1",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
            "publicKeyBase58": "8NNydiyd3KjF46ERwY7rycTBvGKRh4J1BbnYvTYCK283",
        }
    ],
    "capabilityDelegation": [
        {
            "id": "did:example:123#capability-delegation-1",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
            "publicKeyBase58": "8NNydiyd3KjF46ERwY7rycTBvGKRh4J1BbnYvTYCK283",
        }
    ],
    "assertionMethod": [
        {
            "id": "did:example:123#assertion-1",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
            "publicKeyBase58": "8NNydiyd3KjF46ERwY7rycTBvGKRh4J1BbnYvTYCK283",
        }
    ],
    "service": [
        {
            "id": "did:example:123#service-1",
            "type": "example",
            "serviceEndpoint": "https://example.com",
        }
    ],
}

DOC1 = {
    "@context": ["https://w3id.org/did/v1"],
    "id": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
    "authentication": [
        {
            "id": "did:example:123#authentication-1",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
            "publicKeyBase58": "8NNydiyd3KjF46ERwY7rycTBvGKRh4J1BbnYvTYCK283",
        }
    ],
    "capabilityInvocation": [
        {
            "id": "did:example:123#capability-invocation-1",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
            "publicKeyBase58": "8NNydiyd3KjF46ERwY7rycTBvGKRh4J1BbnYvTYCK283",
        }
    ],
    "capabilityDelegation": [
        {
            "id": "did:example:123#capability-delegation-1",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
            "publicKeyBase58": "8NNydiyd3KjF46ERwY7rycTBvGKRh4J1BbnYvTYCK283",
        }
    ],
    "assertionMethod": [
        {
            "id": "did:example:123#assertion-1",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
            "publicKeyBase58": "8NNydiyd3KjF46ERwY7rycTBvGKRh4J1BbnYvTYCK283",
        }
    ],
}

DOC2 = {
    "@context": ["https://w3id.org/did/v1"],
    "id": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
    "controller": ["did:example:123"],
    "authentication": [
        {
            "id": "did:example:123#authentication-1",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
            "publicKeyBase58": "8NNydiyd3KjF46ERwY7rycTBvGKRh4J1BbnYvTYCK283",
        }
    ],
    "capabilityInvocation": [
        {
            "id": "did:example:123#capability-invocation-1",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
            "publicKeyBase58": "8NNydiyd3KjF46ERwY7rycTBvGKRh4J1BbnYvTYCK283",
        }
    ],
    "capabilityDelegation": [
        {
            "id": "did:example:123#capability-delegation-1",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
            "publicKeyBase58": "8NNydiyd3KjF46ERwY7rycTBvGKRh4J1BbnYvTYCK283",
        }
    ],
    "assertionMethod": [
        {
            "id": "did:example:123#assertion-1",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
            "publicKeyBase58": "8NNydiyd3KjF46ERwY7rycTBvGKRh4J1BbnYvTYCK283",
        }
    ],
}

DOC3 = {
    "@context": ["https://w3id.org/did/v1"],
    "id": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
    "controller": ["did:example:123"],
    "authentication": [
        {
            "id": "did:example:123#authentication-1",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
            "publicKeyBase58": "8NNydiyd3KjF46ERwY7rycTBvGKRh4J1BbnYvTYCK283",
        }
    ],
    "capabilityInvocation": [
        {
            "id": "did:example:123#capability-invocation-1",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
            "publicKeyBase58": "8NNydiyd3KjF46ERwY7rycTBvGKRh4J1BbnYvTYCK283",
        }
    ],
    "capabilityDelegation": [
        {
            "id": "did:example:123#capability-delegation-1",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
            "publicKeyBase58": "8NNydiyd3KjF46ERwY7rycTBvGKRh4J1BbnYvTYCK283",
        }
    ],
    "assertionMethod": [
        {
            "id": "did:example:123#assertion-1",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
            "publicKeyBase58": "8NNydiyd3KjF46ERwY7rycTBvGKRh4J1BbnYvTYCK283",
        }
    ],
}

DOC4 = {
    "@context": ["https://w3id.org/did/v1"],
    "id": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
    "controller": ["did:example:123"],
    "verificationMethod": [
        {
            "id": "did:example:123#authentication-1",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
            "publicKeyBase58": "8NNydiyd3KjF46ERwY7rycTBvGKRh4J1BbnYvTYCK283",
        },
        {
            "id": "did:example:123#capability-invocation-1",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
            "publicKeyBase58": "8NNydiyd3KjF46ERwY7rycTBvGKRh4J1BbnYvTYCK283",
        },
        {
            "id": "did:example:123#capability-delegation-1",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
            "publicKeyBase58": "8NNydiyd3KjF46ERwY7rycTBvGKRh4J1BbnYvTYCK283",
        },
        {
            "id": "did:example:123#assertion-1",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
            "publicKeyBase58": "8NNydiyd3KjF46ERwY7rycTBvGKRh4J1BbnYvTYCK283",
        },
    ],
}

DOC5 = {
    "@context": ["https://w3id.org/did/v1"],
    "id": "did:example:123",
}

DOC6 = {
    "@context": ["https://www.w3.org/ns/did/v1"],
    "id": "did:example:123",
    "verificationMethod": [
        {
            "id": "did:example:123#key-0",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:123",
            "publicKeyBase58": "1234",
        }
    ],
    "authentication": [
        "did:example:123#key-0",
        {
            "id": "did:example:123#auth-0",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:123",
            "publicKeyBase58": "abcd",
        },
    ],
    "service": [
        {
            "id": "did:example:123#service-0",
            "type": "example",
            "serviceEndpoint": "https://example.com",
        }
    ],
}

DOC7 = {
    "@context": ["https://www.w3.org/ns/did/v1"],
    "id": "did:example:123",
    "verificationMethod": [
        {
            "id": "did:example:123#keys-0",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:123",
            "publicKeyBase58": "1234",
        }
    ],
    "authentication": [
        "did:example:123#keys-0",
        {
            "id": "did:example:123#auth-0",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:123",
            "publicKeyBase58": "abcd",
        },
    ],
    "service": [
        {
            "id": "did:example:123#service-0",
            "type": "did-communication",
            "serviceEndpoint": "https://example.com",
            "recipientKeys": ["did:example:123#keys-0"],
            "routingKeys": ["did:example:123#keys-1"],
            "priority": 0,
        }
    ],
}

DOC8 = {
    "@context": ["https://www.w3.org/ns/did/v1"],
    "id": "did:example:123",
    "verificationMethod": [
        {
            "id": "did:example:123#keys-0",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:123",
            "publicKeyBase58": "1234",
        }
    ],
    "authentication": [
        "did:example:123#keys-0",
        {
            "id": "did:example:123#auth-0",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:123",
            "publicKeyBase58": "abcd",
        },
    ],
    "service": [
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
    ],
}
DOCS = [DOC0, DOC1, DOC2, DOC3, DOC4, DOC5, DOC6, DOC7, DOC8]

INVALID_DOC0 = {}
INVALID_DOC1 = {
    "verificationMethod": [
        {
            "id": "did:example:123#assertion-1",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
            "publicKeyBase58": "8NNydiyd3KjF46ERwY7rycTBvGKRh4J1BbnYvTYCK283",
        }
    ]
}
INVALID_DOC2 = {
    "@context": "https://www.w3.org/ns/did/v1",
    "id": "did:example:123",
    "verificationMethod": [
        {
            "id": "did:example:123#keys-0",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:123",
            "publicKeyBase58": "1234",
        }
    ],
    "authentication": [
        "did:example:123#keys-0",
        {
            "id": "did:example:123#keys-0",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:123",
            "publicKeyBase58": "abcd",
        },
    ],
    "service": [
        {
            "id": "did:example:123#service-0",
            "type": "example",
            "serviceEndpoint": "https://example.com",
        }
    ],
}

INVALID_DOCS = [INVALID_DOC0, INVALID_DOC1, INVALID_DOC2]


@pytest.mark.parametrize("doc", DOCS)
def test_validate(doc):
    """Test valid docs pass."""
    DIDDocument.deserialize(doc)


@pytest.mark.parametrize("doc", INVALID_DOCS)
def test_fails_invalid(doc):
    """Test invalid docs fail."""
    with pytest.raises((ValueError, DIDDocumentError)):
        DIDDocument.deserialize(doc)


@pytest.mark.parametrize("doc_raw", DOCS)
def test_serialization(doc_raw):
    """Test serialization and deserialization."""
    doc = DIDDocument.deserialize(doc_raw)
    assert doc.serialize() == doc_raw


def test_dereference():
    """Test DID Doc dereferencing a URL."""
    doc = DIDDocument.deserialize(DOC0)
    auth0: VerificationMethod = doc.dereference(DOC0["authentication"][0]["id"])
    assert isinstance(auth0, VerificationMethod)
    assert auth0.serialize() == DOC0["authentication"][0]
    service0: Service = doc.dereference(DOC0["service"][0]["id"])
    assert isinstance(service0, Service)
    assert service0.serialize() == DOC0["service"][0]


@pytest.mark.parametrize("cls", [DIDDocument, NonconformantDocument])
def test_dereference_x(cls):
    doc = cls.deserialize(DOC0)
    with pytest.raises(InvalidDIDUrlError):
        doc.dereference("bogus")

    with pytest.raises(IDNotFoundError):
        doc.dereference("did:example:123#bogus")


def test_vmethod_relationships():
    """Test checking whether a verification method is in a relationship."""
    doc = DIDDocument.deserialize(DOC0)
    auth0: VerificationMethod = doc.dereference(DOC0["authentication"][0]["id"])
    assert isinstance(auth0, VerificationMethod)
    assert doc.authentication
    assert auth0 in doc.authentication
    assert doc.assertion_method
    assert auth0 not in doc.assertion_method


def test_extra_preserved():
    """Test whether extra attributes are preserved."""
    doc_raw = copy.deepcopy(DOC6)
    doc_raw["additionalAttribute"] = {"extra": "junk"}
    doc = DIDDocument.deserialize(doc_raw)
    assert "additionalAttribute" in doc.serialize()


def test_didcomm_service_deserialized():
    """Test whether a DIDCommService is returned when deserialized."""
    doc = DIDDocument.deserialize(DOC7)
    assert isinstance(doc.service[0], DIDCommService)


def test_didcommv2_service_deserialized():
    """Test whether a DIDCommService is returned when deserialized."""
    doc = DIDDocument.deserialize(DOC8)
    assert isinstance(doc.service[0], DIDCommV2Service)


def test_didcommv2_service_dereference():
    """Test whether a DIDCommService is returned when deserialized."""
    doc = DIDDocument.deserialize(DOC8)
    assert isinstance(
        doc.dereference_as(DIDCommV2Service, DOC8["service"][0]["id"]), DIDCommV2Service
    )


def test_programmatic_construction():
    builder = DIDDocumentBuilder("did:example:123")
    assert builder.context == ["https://www.w3.org/ns/did/v1"]
    vmethod1 = builder.verification_method.add(
        Ed25519VerificationKey2018, public_key_base58="1234"
    )
    builder.authentication.reference(vmethod1.id)
    builder.authentication.embed(Ed25519VerificationKey2018, public_key_base58="abcd")
    builder.service.add(type_="example", service_endpoint="https://example.com")
    assert builder.build().serialize() == DOC6


def test_programmatic_construction_didcomm():
    builder = DIDDocumentBuilder("did:example:123")
    key = builder.verification_method.add(
        ExampleVerificationMethod, public_key_example="1234"
    )
    route = builder.verification_method.add(
        ExampleVerificationMethod, public_key_example="abcd"
    )
    another_route = DIDUrl("did:example:123#key-5")
    yet_another_route = "did:example:123#key-6"
    builder.service.add_didcomm(
        service_endpoint="https://example.com",
        recipient_keys=[key],
        routing_keys=[route],
        accept=["didcomm/aip2;env=rfc19"],
    )
    builder.service.add_didcomm(
        service_endpoint="https://example.com",
        recipient_keys=[key],
        routing_keys=[route, another_route, yet_another_route],
    )
    assert builder.build().serialize() == {
        "@context": ["https://www.w3.org/ns/did/v1"],
        "id": "did:example:123",
        "verificationMethod": [
            {
                "id": "did:example:123#key-0",
                "type": "Example",
                "controller": "did:example:123",
                "publicKeyExample": "1234",
            },
            {
                "id": "did:example:123#key-1",
                "type": "Example",
                "controller": "did:example:123",
                "publicKeyExample": "abcd",
            },
        ],
        "service": [
            {
                "id": "did:example:123#service-0",
                "type": "did-communication",
                "serviceEndpoint": "https://example.com",
                "recipientKeys": ["did:example:123#key-0"],
                "routingKeys": ["did:example:123#key-1"],
                "priority": 0,
                "accept": ["didcomm/aip2;env=rfc19"],
            },
            {
                "id": "did:example:123#service-1",
                "type": "did-communication",
                "serviceEndpoint": "https://example.com",
                "recipientKeys": ["did:example:123#key-0"],
                "routingKeys": [
                    "did:example:123#key-1",
                    "did:example:123#key-5",
                    "did:example:123#key-6",
                ],
                "priority": 1,
            },
        ],
    }


def test_all_relationship_builders():
    builder = DIDDocumentBuilder("did:example:123")
    vmethod = builder.verification_method.add(
        Ed25519VerificationKey2018, public_key_base58="12345"
    )
    builder.authentication.reference(vmethod.id)
    builder.authentication.embed(ExampleVerificationMethod, public_key_example="auth")
    builder.assertion_method.reference(vmethod.id)
    builder.assertion_method.embed(ExampleVerificationMethod, public_key_example="assert")
    builder.key_agreement.reference(vmethod.id)
    builder.key_agreement.embed(
        ExampleVerificationMethod, public_key_example="key_agreement"
    )
    builder.capability_invocation.reference(vmethod.id)
    builder.capability_invocation.embed(
        ExampleVerificationMethod, public_key_example="capability_invocation"
    )
    builder.capability_delegation.reference(vmethod.id)
    builder.capability_delegation.embed(
        ExampleVerificationMethod, public_key_example="capability_delegation"
    )

    assert builder.build().serialize() == {
        "@context": ["https://www.w3.org/ns/did/v1"],
        "id": "did:example:123",
        "verificationMethod": [
            {
                "id": "did:example:123#key-0",
                "type": "Ed25519VerificationKey2018",
                "controller": "did:example:123",
                "publicKeyBase58": "12345",
            },
        ],
        "authentication": [
            "did:example:123#key-0",
            {
                "id": "did:example:123#auth-0",
                "type": "Example",
                "controller": "did:example:123",
                "publicKeyExample": "auth",
            },
        ],
        "assertionMethod": [
            "did:example:123#key-0",
            {
                "id": "did:example:123#assert-0",
                "type": "Example",
                "controller": "did:example:123",
                "publicKeyExample": "assert",
            },
        ],
        "keyAgreement": [
            "did:example:123#key-0",
            {
                "id": "did:example:123#key-agreement-0",
                "type": "Example",
                "controller": "did:example:123",
                "publicKeyExample": "key_agreement",
            },
        ],
        "capabilityInvocation": [
            "did:example:123#key-0",
            {
                "id": "did:example:123#capability-invocation-0",
                "type": "Example",
                "controller": "did:example:123",
                "publicKeyExample": "capability_invocation",
            },
        ],
        "capabilityDelegation": [
            "did:example:123#key-0",
            {
                "id": "did:example:123#capability-delegation-0",
                "type": "Example",
                "controller": "did:example:123",
                "publicKeyExample": "capability_delegation",
            },
        ],
    }


def test_relationship_builder_ref_x():
    builder = DIDDocumentBuilder("did:example:123")
    with pytest.raises(ValueError):
        builder.authentication.reference("123")


def test_builder_from_doc():
    doc = DIDDocument.deserialize(DOC6)
    builder = DIDDocumentBuilder.from_doc(doc)
    builder.verification_method.add(ExampleVerificationMethod, public_key_example="1234")
    assert len(builder.build().serialize()["verificationMethod"]) == 2


def test_builder_from_doc_remove():
    doc = DIDDocument.deserialize(DOC6)
    builder = DIDDocumentBuilder.from_doc(doc)
    vmethod = builder.verification_method.add(
        ExampleVerificationMethod, public_key_example="1234"
    )
    assert len(builder.build().serialize()["verificationMethod"]) == 2
    builder.verification_method.remove(vmethod)
    assert len(builder.build().serialize()["verificationMethod"]) == 1
    service = builder.service.add("example", "http://example.com", "ident")
    assert len(builder.build().serialize()["service"]) == 2
    builder.service.remove(service)
    assert len(builder.build().serialize()["service"]) == 1
    assertion = builder.assertion_method.add(
        ExampleVerificationMethod,
        ident="123",
        public_key_example="1234",
    )
    assert len(builder.build().serialize()["assertionMethod"]) == 1
    builder.assertion_method.remove(assertion)
    assert "assertionMethod" not in builder.build().serialize()


def test_key_rotation_from_doc():
    doc = DIDDocument.deserialize(DOC6)
    vmethod0 = doc.dereference("did:example:123#key-0")

    builder = DIDDocumentBuilder.from_doc(doc)
    builder.verification_method.remove(vmethod0)
    builder.authentication.remove(vmethod0.id)
    assert builder.build().serialize() == {
        "@context": ["https://www.w3.org/ns/did/v1"],
        "id": "did:example:123",
        "authentication": [
            {
                "id": "did:example:123#auth-0",
                "type": "Ed25519VerificationKey2018",
                "controller": "did:example:123",
                "publicKeyBase58": "abcd",
            },
        ],
        "service": [
            {
                "id": "did:example:123#service-0",
                "type": "example",
                "serviceEndpoint": "https://example.com",
            }
        ],
    }


def test_build_and_dereference():
    builder = DIDDocumentBuilder("did:example:123")
    builder.verification_method.add(
        Ed25519VerificationKey2018, public_key_base58="test", ident="1"
    )
    doc = builder.build()
    assert doc.dereference("#1")


def test_dereference_and_membership_check():
    doc_raw = {
        "@context": "https://www.w3.org/ns/did/v1",
        "id": "did:example:123",
        "authentication": [
            {
                "id": "did:example:123#keys-0",
                "type": "Ed25519VerificationKey2018",
                "controller": "did:example:123",
                "publicKeyBase58": "1234",
            },
        ],
        "assertionMethod": [
            {
                "id": "did:example:123#keys-0",
                "type": "Ed25519VerificationKey2018",
                "controller": "did:example:123",
                "publicKeyBase58": "1234",
            },
        ],
        "service": [
            {
                "id": "did:example:123#service-0",
                "type": "example",
                "serviceEndpoint": "https://example.com",
            }
        ],
    }
    doc = DIDDocument.deserialize(doc_raw)
    vmethod = doc.dereference("did:example:123#keys-0")
    assert not doc.verification_method
    assert vmethod in doc.authentication
    assert vmethod in doc.assertion_method


@pytest.mark.parametrize("cls", [DIDDocument, NonconformantDocument])
def test_relative_ids(cls):
    doc_raw = {
        "@context": "https://www.w3.org/ns/did/v1",
        "id": "did:example:123",
        "authentication": [
            {
                "id": "#keys-0",
                "type": "Ed25519VerificationKey2018",
                "controller": "did:example:123",
                "publicKeyBase58": "1234",
            },
        ],
        "assertionMethod": [
            {
                "id": "#keys-1",
                "type": "Ed25519VerificationKey2018",
                "controller": "did:example:123",
                "publicKeyBase58": "abcd",
            },
        ],
        "service": [
            {
                "id": "#service-0",
                "type": "example",
                "serviceEndpoint": "https://example.com",
            }
        ],
    }
    doc = cls.deserialize(doc_raw)
    assert doc.dereference("did:example:123#keys-0") == doc.dereference("#keys-0")
    assert doc.dereference("did:example:123#keys-1") == doc.dereference("#keys-1")
    assert doc.dereference("did:example:123#service-0") == doc.dereference("#service-0")


def test_listify():
    doc = DIDDocumentRoot.deserialize({"id": "did:example:123", "controller": None})
    assert doc.controller is None


def test_default_context_should_not_mutate():
    # given

    doc_builder = DIDDocumentBuilder("did:example:123")
    # save a copy of the default context before mutating the document's contexts
    original_default_context = list(doc_builder.context)

    # when

    doc_builder.context.append("https://some-required-context")

    # then
    assert DIDDocumentBuilder("did:example:123").context == original_default_context
