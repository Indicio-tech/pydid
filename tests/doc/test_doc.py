"""Test DIDDocument object."""

import copy

import pytest
from voluptuous import MultipleInvalid

from pydid.doc.doc import DIDDocument, DIDDocumentBuilder
from pydid.doc.verification_method import VerificationMethod, VerificationSuite
from pydid.doc.service import Service

DOC0 = {
    "@context": "https://w3id.org/did/v0.11",
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
    "@context": "https://w3id.org/did/v1",
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
    "@context": "https://w3id.org/did/v1",
    "id": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
    "controller": "did:example:123",
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
    "@context": "https://w3id.org/did/v1",
    "id": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
    "controller": "did:example:123",
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
    "@context": "https://w3id.org/did/v1",
    "id": "did:example:z6Mkmpe2DyE4NsDiAb58d75hpi1BjqbH6wYMschUkjWDEEuR",
    "controller": "did:example:123",
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
    "@context": "https://w3id.org/did/v1",
    "id": "did:example:123",
}

DOC6 = {
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

DOCS = [DOC0, DOC1, DOC2, DOC3, DOC4, DOC5, DOC6]

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

INVALID_DOCS = [INVALID_DOC0, INVALID_DOC1]


@pytest.mark.parametrize("doc", DOCS)
def test_validate(doc):
    """Test valid docs pass."""
    DIDDocument.validate(doc)


@pytest.mark.parametrize("doc", INVALID_DOCS)
def test_fails_invalid(doc):
    """Test invalid docs fail."""
    with pytest.raises(MultipleInvalid):
        DIDDocument.validate(doc)


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


def test_vmethod_relationships():
    """Test checking whether a verification method is in a relationship."""
    doc = DIDDocument.deserialize(DOC0)
    auth0: VerificationMethod = doc.dereference(DOC0["authentication"][0]["id"])
    assert isinstance(auth0, VerificationMethod)
    assert auth0 in doc.authentication
    assert auth0 not in doc.assertion_method


def test_extra_preserved():
    """Test whether extra attributes are preserved."""
    doc_raw = copy.deepcopy(DOC6)
    doc_raw["additionalAttribute"] = {"extra": "junk"}
    doc = DIDDocument.deserialize(doc_raw)
    assert "additionalAttribute" in doc.serialize()


def test_programmatic_construction():
    ed25519 = VerificationSuite("Ed25519VerificationKey2018", "publicKeyBase58")
    builder = DIDDocumentBuilder("did:example:123")
    assert builder.context == ["https://www.w3.org/ns/did/v1"]
    with builder.verification_methods(default_suite=ed25519) as vmethods:
        vmethod1 = vmethods.add("1234")
    with builder.authentication(default_suite=ed25519) as auth:
        auth.reference(vmethod1.id)
        auth.embed("abcd")
    with builder.services() as services:
        services.add(type_="example", endpoint="https://example.com")
    assert builder.build().serialize() == DOC6


def test_builder_from_doc():
    doc = DIDDocument.deserialize(DOC6)
    builder = doc.to_builder()
    with builder.verification_methods() as vmethods:
        vmethods.add(
            suite=VerificationSuite("Example", "publicKeyExample"), material="1234"
        )
    assert len(builder.build().serialize()["verificationMethod"]) == 2


def test_deserialization_options():
    pytest.fail("Not implemented.")
