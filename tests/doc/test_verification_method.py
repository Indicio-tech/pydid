"""Test VerificationMethod."""

import pytest
from voluptuous import MultipleInvalid

from pydid.did import DID
from pydid.did_url import DIDUrl
from pydid.doc.verification_method import VerificationMethod, VerificationSuite
from pydid.doc.verification_method_options import VerificationMethodOptions

VMETHOD0 = {
    "id": "did:example:123#keys-1",
    "type": "Ed25519Signature2018",
    "controller": "did:example:123",
    "publicKeyBase58": "12345",
}
VMETHOD1 = {
    "id": "did:example:123#keys-1",
    "type": "Ed25519Signature2018",
    "controller": "did:example:123",
    "publicKeyPem": "12345",
}
VMETHOD2 = {
    "id": "did:example:123#keys-1",
    "type": "Ed25519Signature2018",
    "controller": "did:example:123",
    "publicKeyJwk": {
        "crv": "Ed25519",
        "x": "VCpo2LMLhn6iWku8MKvSLg2ZAoC-nlOyPVQaO3FxVeQ",
        "kty": "OKP",
        "kid": "_Qq0UL2Fq651Q0Fjd6TvnYE-faHiOpRlPVQcY_-tA4A",
    },
}
VMETHODS = [VMETHOD0, VMETHOD1, VMETHOD2]

INVALID_VMETHOD0 = {
    "id": "did:example:123#keys-1",
    "type": "Ed25519Signature2018",
    "controller": "did:example:123",
}

INVALID_VMETHOD1 = {
    "id": "did:example:123#keys-1",
    "type": "Ed25519Signature2018",
    "controller": "did:example:123",
    "something": "random",
}
INVALID_VMETHOD2 = {
    "id": "did:example:123",
    "type": "Ed25519Signature2018",
    "controller": "did:example:123",
    "publicKeyPem": "12345",
}

INVALID_VMETHODS = [
    INVALID_VMETHOD0,
    INVALID_VMETHOD1,
    INVALID_VMETHOD2,
]


@pytest.mark.parametrize("vmethod", VMETHODS)
def test_validates_valid(vmethod):
    VerificationMethod.validate(vmethod)


@pytest.mark.parametrize("vmethod", INVALID_VMETHODS)
def test_fails_validate_invalid(vmethod):
    with pytest.raises(MultipleInvalid):
        VerificationMethod.validate(vmethod)


@pytest.mark.parametrize("vmethod_raw", VMETHODS)
def test_serialization(vmethod_raw):
    vmethod = VerificationMethod.deserialize(vmethod_raw)
    assert vmethod.serialize() == vmethod_raw


@pytest.mark.parametrize("invalid_vmethod_raw", INVALID_VMETHODS)
def test_serialization_x(invalid_vmethod_raw):
    with pytest.raises(MultipleInvalid):
        VerificationMethod.deserialize(invalid_vmethod_raw)


def test_deserialized_member_types():
    vmethod = VerificationMethod.deserialize(VMETHOD0)
    assert isinstance(vmethod.id, DIDUrl)
    assert isinstance(vmethod.controller, DID)


def test_init_mapping():
    vmethod = VerificationMethod(
        id_=DIDUrl("did:example:123", fragment="keys-1"),
        suite=VerificationSuite("TestType", "publicKeyBase58"),
        controller=DID("did:example:123"),
        material="12345",
    )
    assert isinstance(vmethod.id, DIDUrl)
    assert str(vmethod.id) == "did:example:123#keys-1"
    assert isinstance(vmethod.controller, DID)
    assert str(vmethod.controller) == "did:example:123"


def test_init_errors_raised():
    with pytest.raises(ValueError) as err:
        VerificationMethod(id_=123, suite=123, controller=123, material="12345")
        assert "expected DID" in err
        assert "expected DIDUrl" in err
        assert "expected VerificationSuite" in err


def test_option_allow_type_list():
    vmethod = VerificationMethod.deserialize(
        {
            "id": "did:example:123#keys-1",
            "type": ["Ed25519Signature2018"],
            "controller": "did:example:123",
            "publicKeyBase58": "12345",
        },
        options={VerificationMethodOptions.allow_type_list},
    )
    assert vmethod.type == "Ed25519Signature2018"


def test_option_allow_controller_list():
    vmethod = VerificationMethod.deserialize(
        {
            "id": "did:example:123#keys-1",
            "type": "Ed25519Signature2018",
            "controller": ["did:example:123"],
            "publicKeyBase58": "12345",
        },
        options={VerificationMethodOptions.allow_controller_list},
    )
    assert vmethod.controller == "did:example:123"


def test_option_allow_missing_controller():
    vmethod = VerificationMethod.deserialize(
        {
            "id": "did:example:123#keys-1",
            "type": "Ed25519Signature2018",
            "publicKeyBase58": "12345",
        },
        options={VerificationMethodOptions.allow_missing_controller},
    )
    assert vmethod.controller == "did:example:123"
    with pytest.raises(MultipleInvalid):
        vmethod = VerificationMethod.deserialize(
            {
                "type": "Ed25519Signature2018",
                "publicKeyBase58": "12345",
            },
            options={VerificationMethodOptions.allow_missing_controller},
        )
