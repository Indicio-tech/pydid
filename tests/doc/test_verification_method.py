"""Test VerificationMethod."""

import pytest

from voluptuous import MultipleInvalid
from pydid.doc.verification_method import VerificationMethod

VMETHOD0 = {
    "id": "did:example:123#keys-1",
    "type": "Ed25519Signature2018",
    "controller": "did:example:123",
    "publicKeyBase58": "12345"
}
VMETHOD1 = {
    "id": "did:example:123#keys-1",
    "type": "Ed25519Signature2018",
    "controller": "did:example:123",
    "publicKeyPem": "12345"
}
VMETHOD2 = {
    "id": "did:example:123#keys-1",
    "type": "Ed25519Signature2018",
    "controller": "did:example:123",
    "publicKeyJwk": {
        "crv": "Ed25519",
        "x": "VCpo2LMLhn6iWku8MKvSLg2ZAoC-nlOyPVQaO3FxVeQ",
        "kty": "OKP",
        "kid": "_Qq0UL2Fq651Q0Fjd6TvnYE-faHiOpRlPVQcY_-tA4A"
    }
}
VMETHODS = [
    VMETHOD0, VMETHOD1, VMETHOD2
]

INVALID_VMETHOD0 = {
    "id": "did:example:123#keys-1",
    "type": "Ed25519Signature2018",
    "controller": "did:example:123",
}

INVALID_VMETHOD1 = {
    "id": "did:example:123#keys-1",
    "type": "Ed25519Signature2018",
    "controller": "did:example:123",
    "something": "random"
}
INVALID_VMETHOD2 = {
    "id": "did:example:123",
    "type": "Ed25519Signature2018",
    "controller": "did:example:123",
    "publicKeyPem": "12345"
}

INVALID_VMETHODS = [
    INVALID_VMETHOD0,
    INVALID_VMETHOD1,
    INVALID_VMETHOD2,
]


@pytest.mark.parametrize("vmethod", VMETHODS)
def test_validates_valid(vmethod):
    VerificationMethod.Schema(vmethod)


@pytest.mark.parametrize("vmethod", INVALID_VMETHODS)
def test_fails_validate_invalid(vmethod):
    with pytest.raises(MultipleInvalid):
        VerificationMethod.Schema(vmethod)
