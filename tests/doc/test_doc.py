"""Test DIDDocument object."""

from collections import namedtuple
import copy
from pydid.validation import coerce
from typing import cast

import pytest

from pydid.did_url import InvalidDIDUrlError
from pydid.doc import doc_corrections
from pydid.doc.doc import (
    DIDDocument,
    DIDDocumentError,
    IDNotFoundError,
)
from pydid.doc.builder import (
    DIDDocumentBuilder,
    ServiceBuilder,
    VerificationMethodBuilder,
)
from pydid.doc.service import Service
from pydid.doc.service import DIDCommService
from pydid.doc.verification_method import VerificationMethod

VerificationSuite = namedtuple(
    "VerificationSuite", ["type", "verification_material_prop"]
)

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

DOCS = [DOC0, DOC1, DOC2, DOC3, DOC4, DOC5, DOC6, DOC7]

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


def test_dereference_x():
    doc = DIDDocument.deserialize(DOC0)
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


def test_programmatic_construction():
    ed25519 = VerificationSuite("Ed25519VerificationKey2018", "publicKeyBase58")
    builder = DIDDocumentBuilder("did:example:123")
    assert builder.context == ["https://www.w3.org/ns/did/v1"]
    with builder.verification_methods.defaults(suite=ed25519) as vmethods:
        vmethod1 = vmethods.add("1234")
    with builder.authentication.defaults(suite=ed25519) as auth:
        auth.reference(vmethod1.id)
        auth.embed("abcd")
    with builder.services.defaults() as services:
        services.add(type_="example", endpoint="https://example.com")
    assert builder.build().serialize() == DOC6


def test_programmatic_construction_x_no_suite():
    builder = DIDDocumentBuilder("did:example:123")
    with pytest.raises(ValueError):
        with builder.verification_methods.defaults() as vmethods:
            vmethods.add("1234")


def test_programmatic_construction_didcomm():
    builder = DIDDocumentBuilder("did:example:123")
    with builder.verification_methods.defaults(
        suite=VerificationSuite("Example", "publicKeyBase58")
    ) as vmethods:
        key = vmethods.add("1234")
        route = vmethods.add("abcd")
    with builder.services.defaults() as services:
        services = cast(ServiceBuilder, services)
        services.add_didcomm(
            endpoint="https://example.com", recipient_keys=[key], routing_keys=[route]
        )
    assert builder.build().serialize() == {
        "@context": "https://www.w3.org/ns/did/v1",
        "id": "did:example:123",
        "verificationMethod": [
            {
                "id": "did:example:123#keys-0",
                "type": "Example",
                "controller": "did:example:123",
                "publicKeyBase58": "1234",
            },
            {
                "id": "did:example:123#keys-1",
                "type": "Example",
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


def test_all_relationship_builders():
    builder = DIDDocumentBuilder("did:example:123")
    with builder.verification_methods.defaults() as vmethods:
        vmethods = cast(VerificationMethodBuilder, vmethods)
        vmethod = vmethods.add(
            suite=VerificationSuite("Ed25519VerificationKey2018", "publicKeyBase58"),
            material="12345",
        )
    with builder.authentication.defaults() as auth:
        auth.reference(vmethod.id)
        auth.embed(
            suite=VerificationSuite("Example", "publicKeyExample"), material="auth"
        )
    with builder.assertion_method.defaults() as assertion:
        assertion.reference(vmethod.id)
        assertion.embed(
            suite=VerificationSuite("Example", "publicKeyExample"), material="assert"
        )
    with builder.key_agreement.defaults() as key_agreement:
        key_agreement.reference(vmethod.id)
        key_agreement.embed(
            suite=VerificationSuite("Example", "publicKeyExample"),
            material="key_agreement",
        )
    with builder.capability_invocation.defaults() as capability_invocation:
        capability_invocation.reference(vmethod.id)
        capability_invocation.embed(
            suite=VerificationSuite("Example", "publicKeyExample"),
            material="capability_invocation",
        )
    with builder.capability_delegation.defaults() as capability_delegation:
        capability_delegation.reference(vmethod.id)
        capability_delegation.embed(
            suite=VerificationSuite("Example", "publicKeyExample"),
            material="capability_delegation",
        )

    assert builder.build().serialize() == {
        "@context": "https://www.w3.org/ns/did/v1",
        "id": "did:example:123",
        "verificationMethod": [
            {
                "id": "did:example:123#keys-0",
                "type": "Ed25519VerificationKey2018",
                "controller": "did:example:123",
                "publicKeyBase58": "12345",
            },
        ],
        "authentication": [
            "did:example:123#keys-0",
            {
                "id": "did:example:123#auth-0",
                "type": "Example",
                "controller": "did:example:123",
                "publicKeyExample": "auth",
            },
        ],
        "assertionMethod": [
            "did:example:123#keys-0",
            {
                "id": "did:example:123#assert-0",
                "type": "Example",
                "controller": "did:example:123",
                "publicKeyExample": "assert",
            },
        ],
        "keyAgreement": [
            "did:example:123#keys-0",
            {
                "id": "did:example:123#key-agreement-0",
                "type": "Example",
                "controller": "did:example:123",
                "publicKeyExample": "key_agreement",
            },
        ],
        "capabilityInvocation": [
            "did:example:123#keys-0",
            {
                "id": "did:example:123#capability-invocation-0",
                "type": "Example",
                "controller": "did:example:123",
                "publicKeyExample": "capability_invocation",
            },
        ],
        "capabilityDelegation": [
            "did:example:123#keys-0",
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
        with builder.authentication.defaults() as auth:
            auth.reference("123")


def test_vmethod_builder_x_no_ident():
    builder = DIDDocumentBuilder("did:example:123")
    with pytest.raises(ValueError):
        builder.authentication.embed(
            "1234", suite=VerificationSuite("Example", "publicKeyExample")
        )


def test_builder_from_doc():
    doc = DIDDocument.deserialize(DOC6)
    builder = DIDDocumentBuilder.from_doc(doc)
    with builder.verification_methods.defaults() as vmethods:
        vmethods.add(
            suite=VerificationSuite("Example", "publicKeyExample"), material="1234"
        )
    assert len(builder.build().serialize()["verificationMethod"]) == 2


def test_builder_from_doc_remove():
    doc = DIDDocument.deserialize(DOC6)
    builder = DIDDocumentBuilder.from_doc(doc)
    with builder.verification_methods.defaults() as vmethods:
        vmethod = vmethods.add(
            suite=VerificationSuite("Example", "publicKeyExample"), material="1234"
        )
    assert len(builder.build().serialize()["verificationMethod"]) == 2
    builder.verification_methods.remove(vmethod)
    assert len(builder.build().serialize()["verificationMethod"]) == 1
    service = builder.services.add("example", "http://example.com", "ident")
    assert len(builder.build().serialize()["service"]) == 2
    builder.services.remove(service)
    assert len(builder.build().serialize()["service"]) == 1
    assertion = builder.assertion_method.add(
        ident="123",
        suite=VerificationSuite("Example", "publicKeyExample"),
        material="1234",
    )
    assert len(builder.build().serialize()["assertionMethod"]) == 1
    builder.assertion_method.remove(assertion)
    assert "assertionMethod" not in builder.build().serialize()


def test_key_rotation_from_doc():
    doc = DIDDocument.deserialize(DOC6)
    vmethod0 = doc.dereference("did:example:123#keys-0")

    builder = DIDDocumentBuilder.from_doc(doc)
    builder.verification_methods.remove(vmethod0)
    builder.authentication.remove(vmethod0.id)
    assert builder.build().serialize() == {
        "@context": "https://www.w3.org/ns/did/v1",
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


def test_correction_insert_missing_ids_x():
    MyDIDDocument = coerce([doc_corrections.insert_missing_ids])(DIDDocument)
    doc_raw = {
        "@context": "https://www.w3.org/ns/did/v1",
        "authentication": [
            {
                "type": "Ed25519VerificationKey2018",
                "controller": "did:example:123",
                "publicKeyBase58": "1234",
            },
        ],
    }
    with pytest.raises(ValueError):
        MyDIDDocument.deserialize(doc_raw)
