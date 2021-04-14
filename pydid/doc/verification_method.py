"""DID Doc Verification Method."""

from typing import Type, Union
from inflection import underscore

from pydantic import create_model
from typing_extensions import Literal

from ..did import DID
from ..did_url import DIDUrl
from .resource import Resource


class VerificationMethod(Resource):
    """Representation of DID Document Verification Methods."""

    id: DIDUrl
    type: str
    controller: DID

    @classmethod
    def suite(cls: Type, typ: str, material: str, material_type: Type):
        """Return a subclass of VerificationMethod for a given type."""
        return create_model(
            typ,
            __module__=cls.__module__,
            __base__=cls,
            type=(Literal[typ], ...),
            **{underscore(material): (material_type, ...)}
        )


# Verification Method Suites registered in DID Spec

Ed25519Verification2018 = VerificationMethod.suite(
    "Ed25519Verification2018", "publicKeyBase58", str
)

OpenPgpVerificationKey2019 = VerificationMethod.suite(
    "OpenPgpVerificationKey2019", "publicKeyPem", str
)

JsonWebKey2020 = VerificationMethod.suite("JsonWebKey2020", "publicKeyJwk", dict)

EcdsaSecp256k1VerificationKey2019 = VerificationMethod.suite(
    "EcdsaSecp256k1VerificationKey2019", "publicKeyJwk", dict
)

Bls1238G1Key2020 = VerificationMethod.suite("Bls1238G1Key2020", "publicKeyBase58", str)

Bls1238G2Key2020 = VerificationMethod.suite("Bls1238G2Key2020", "publicKeyBase58", str)

GpgVerifcationKey2020 = VerificationMethod.suite(
    "GpgVerifcationKey2020", "publicKeyGpg", str
)

RsaVerificationKey2018 = VerificationMethod.suite(
    "RsaVerificationKey2018", "publicKeyJwk", str
)

X25519KeyAgreementKey2019 = VerificationMethod.suite(
    "X25519KeyAgreementKey2019", "publicKeyBase58", str
)

SchnorrSecp256k1VerificationKey2019 = VerificationMethod.suite(
    "SchnorrSecp256k1VerificationKey2019", "publicKeyJwk", dict
)

EcdsaSecp256k1RecoveryMethod2020 = VerificationMethod.suite(
    "EcdsaSecp256k1RecoveryMethod2020", "publicKeyJwk", str
)


class UnsupportedVerificationMethod(VerificationMethod):
    """Model representing unsupported verification methods."""


class UnknownVerificationMethod(VerificationMethod):
    """Model representing unknown verification methods."""


KnownVerificationMethods = Union[
    Ed25519Verification2018,
    OpenPgpVerificationKey2019,
    JsonWebKey2020,
    EcdsaSecp256k1VerificationKey2019,
    Bls1238G1Key2020,
    Bls1238G2Key2020,
    GpgVerifcationKey2020,
    RsaVerificationKey2018,
    X25519KeyAgreementKey2019,
    SchnorrSecp256k1VerificationKey2019,
    EcdsaSecp256k1RecoveryMethod2020,
]
