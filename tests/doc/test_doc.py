"""Test DIDDocument object."""

import pytest

from voluptuous import MultipleInvalid
from pydid.doc.doc import DIDDocument
from pydid.doc.verification_method import VerificationMethod

DOC0 = {
    "@context": ["https://w3id.org/did/v0.11", "https://w3id.org/veres-one/v1"],
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
    "@context": "https://w3id.org/did/v1",
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
    "@context": "https://w3id.org/did/v1",
    "id": "did:example:123",
}

DOC6 = {
    "@context": "https://w3id.org/did/v1",
    "id": "did:example:123",
    "verificationMethod": [
        {
            "id": "did:example:123#keys-1",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:123",
            "publicKeyBase58": "1234",
        }
    ],
    "authentication": [
        "did:example:123#keys-1",
        {
            "id": "did:example:123#auth-1",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:123",
            "publicKeyBase58": "abcd",
        },
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
