"""Test VerificationMethod."""

import pytest
from typing_extensions import Literal

from pydid.did import DID
from pydid.did_url import DIDUrl
from pydid.verification_method import (
    Base58VerificationMethod,
    Ed25519VerificationKey2018,
    VerificationMaterialUnknown,
    VerificationMethod,
)

VMETHOD0 = {
    "id": "did:example:123#keys-1",
    "type": "Ed25519VerificationKey2018",
    "controller": "did:example:123",
    "publicKeyBase58": "12345",
}
VMETHOD1 = {
    "id": "did:example:123#keys-1",
    "type": "OpenPgpVerificationKey2019",
    "controller": "did:example:123",
    "publicKeyPem": "12345",
}
VMETHOD2 = {
    "id": "did:example:123#keys-1",
    "type": "JsonWebKey2020",
    "controller": "did:example:123",
    "publicKeyJwk": {
        "crv": "Ed25519",
        "x": "VCpo2LMLhn6iWku8MKvSLg2ZAoC-nlOyPVQaO3FxVeQ",
        "kty": "OKP",
        "kid": "_Qq0UL2Fq651Q0Fjd6TvnYE-faHiOpRlPVQcY_-tA4A",
    },
}
VMETHOD3 = {
    "id": "did:example:123#keys-1",
    "type": "Ed25519Signature2018",
    "controller": "did:example:123",
    "something": "random",
}

VMETHODS = [VMETHOD0, VMETHOD1, VMETHOD2, VMETHOD3]

INVALID_VMETHOD0 = {
    "id": "did:example:123#keys-1",
    "type": "Ed25519Signature2018",
    "controller": "did:example:123",
}

INVALID_VMETHOD1 = {
    "id": "did:example:123",
    "type": "Ed25519Signature2018",
    "controller": "did:example:123",
    "publicKeyPem": "12345",
}

INVALID_VMETHODS = [
    INVALID_VMETHOD0,
    INVALID_VMETHOD1,
]


@pytest.mark.parametrize("vmethod_raw", VMETHODS)
def test_serialization(vmethod_raw):
    vmethod = VerificationMethod.deserialize(vmethod_raw)
    assert vmethod.id == DIDUrl.parse(vmethod_raw["id"])
    assert vmethod.type == vmethod_raw["type"]
    assert vmethod.controller == DID(vmethod_raw["controller"])
    assert vmethod.serialize() == vmethod_raw


@pytest.mark.parametrize("invalid_vmethod_raw", INVALID_VMETHODS)
def test_serialization_x(invalid_vmethod_raw):
    with pytest.raises(ValueError):
        VerificationMethod.deserialize(invalid_vmethod_raw)


def test_deserialized_member_types():
    vmethod = VerificationMethod.deserialize(VMETHOD0)
    assert isinstance(vmethod.id, DIDUrl)
    assert isinstance(vmethod.controller, DID)


def test_suite_creation():
    MyVerificationMethod = VerificationMethod.suite(
        "MyVerificationMethod", "publicKeyExample", str
    )
    vmethod = MyVerificationMethod(
        id="did:example:123#test",
        type="MyVerificationMethod",
        controller="did:example:123",
        public_key_example="test",
    )
    assert vmethod.material == "test"


def test_generic_verification_method_has_props():
    vmethod = VerificationMethod(
        id="did:example:123#test",
        type="MyVerificationMethod",
        controller="did:example:123",
        publicKeyExample="test",
    )
    assert hasattr(vmethod, "publicKeyExample")
    assert "publicKeyExample" in vmethod.serialize()


def test_validator_allow_type_list():
    vmethod = VerificationMethod.deserialize(
        {
            "id": "did:example:123#keys-1",
            "type": ["Ed25519Signature2018"],
            "controller": "did:example:123",
            "publicKeyBase58": "12345",
        }
    )
    assert vmethod.type == "Ed25519Signature2018"


def test_validator_allow_controller_list():
    vmethod = VerificationMethod.deserialize(
        {
            "id": "did:example:123#keys-1",
            "type": "Ed25519Signature2018",
            "controller": ["did:example:123"],
            "publicKeyBase58": "12345",
        },
    )
    assert vmethod.controller == "did:example:123"


def test_validator_allow_missing_controller():
    vmethod = VerificationMethod.deserialize(
        {
            "id": "did:example:123#keys-1",
            "type": "Ed25519Signature2018",
            "publicKeyBase58": "12345",
        },
    )
    assert vmethod.controller == "did:example:123"
    with pytest.raises(ValueError):
        vmethod = VerificationMethod.deserialize(
            {
                "type": "Ed25519Signature2018",
                "publicKeyBase58": "12345",
            },
        )


def test_make():
    did = DID("did:example:123")
    kwargs = {"id_": did.ref("1"), "controller": did, "material": "test"}
    with pytest.raises(VerificationMaterialUnknown):
        VerificationMethod.make(**kwargs)

    vmethod = Ed25519VerificationKey2018.make(**kwargs)
    assert "publicKeyBase58" in vmethod.serialize()

    class ExampleVerificationMethod(Base58VerificationMethod):
        type: Literal["Example"]

    vmethod = ExampleVerificationMethod.make(**kwargs)
    assert "publicKeyBase58" in vmethod.serialize()

    ExampleVerificationMethod = VerificationMethod.suite(
        "Example", "publicKeyBase58", str
    )

    vmethod = ExampleVerificationMethod.make(**kwargs)
    assert "publicKeyBase58" in vmethod.serialize()
