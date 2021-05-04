"""DID Doc Verification Method."""

from typing import Type, Union
from inflection import underscore

from pydantic import create_model
from pydantic.class_validators import root_validator, validator
from typing_extensions import Literal

from ..did import DID
from ..did_url import DIDUrl, InvalidDIDUrlError
from .resource import Resource


class VerificationMaterialUnknown(NotImplementedError):
    """Raised when verification material is unknown but access is attempted."""


class VerificationMethod(Resource):
    """Representation of DID Document Verification Methods."""

    id: DIDUrl
    type: str
    controller: DID

    @property
    def material(self):
        """Return material."""
        raise VerificationMaterialUnknown(
            "Verification Material was not specified on class"
        )

    @classmethod
    def suite(cls: Type, typ: str, material: str, material_type: Type):
        """Return a subclass of VerificationMethod for a given type."""
        model = create_model(
            typ,
            __module__=cls.__module__,
            __base__=cls,
            type=(Literal[typ], ...),
            **{underscore(material): (material_type, ...)},
        )
        model.material = property(lambda self: getattr(self, underscore(material)))
        return model

    @validator("type", pre=True)
    @classmethod
    def _allow_type_list(cls, value: Union[str, list]):
        """Unwrap type list.

        This validator handles a common DID Document mutation.
        """
        if isinstance(value, list):
            return value[0]
        return value

    @validator("controller", pre=True)
    @classmethod
    def _allow_controller_list(cls, value: Union[str, list]):
        """Unwrap controller list.

        This validator handles a common DID Document mutation.
        """
        if isinstance(value, list):
            return value[0]
        return value

    @root_validator(pre=True)
    @classmethod
    def _allow_missing_controller(cls, values: dict):
        """Derive controller value from ID.

        This validator handles a common DID Document mutation.
        """
        if "id" not in values:
            raise ValueError(
                "Could not derive controller: no id present in verification method"
            )
        if "controller" not in values:
            try:
                ident = DIDUrl.parse(values["id"])
            except InvalidDIDUrlError:
                return values
            else:
                values["controller"] = ident.did
        return values

    @root_validator(pre=True)
    @classmethod
    def _method_appears_to_contain_material(cls, values: dict):
        """Validate that the method appears to contain verification materla."""
        if len(values) < 4:
            raise ValueError(
                "Key material expected, only found id, type, and controller"
            )
        return values


# Verification Method Suites registered in DID Spec


class Base58VerificationMethod(VerificationMethod):
    """Verification Method where material is base58."""

    public_key_base58: str

    @property
    def material(self):
        """Return material."""
        return self.public_key_base58


class PemVerificationMethod(VerificationMethod):
    """Verification Method where material is pem."""

    public_key_pem: str

    @property
    def material(self):
        """Return material."""
        return self.public_key_pem


class JwkVerificationMethod(VerificationMethod):
    """Verification Method where material is jwk."""

    public_key_jwk: dict

    @property
    def material(self):
        """Return material."""
        return self.public_key_jwk


class Ed25519Verification2018(Base58VerificationMethod):
    """Ed25519Verification2018 VerificationMethod."""

    type: Literal["Ed25519Verification2018"]


class OpenPgpVerificationKey2019(PemVerificationMethod):
    """OpenPgpVerificationKey2019 VerificationMethod."""

    type: Literal["OpenPgpVerificationKey2019"]


class JsonWebKey2020(JwkVerificationMethod):
    """JsonWebKey2020 VerificationMethod."""

    type: Literal["JsonWebKey2020"]


class EcdsaSecp256k1VerificationKey2019(JwkVerificationMethod):
    """EcdsaSecp256k1VerificationKey2019 VerificationMethod."""

    type: Literal["EcdsaSecp256k1VerificationKey2019"]


class Bls1238G1Key2020(Base58VerificationMethod):
    """Bls1238G1Key2020 VerificationMethod."""

    type: Literal["Bls1238G1Key2020"]


class Bls1238G2Key2020(Base58VerificationMethod):
    """Bls1238G2Key2020 VerificationMethod."""

    type: Literal["Bls1238G2Key2020"]


class GpgVerifcationKey2020(VerificationMethod):
    """GpgVerifcationKey2020 VerificationMethod."""

    type: Literal["GpgVerifcationKey2020"]
    public_key_gpg: str

    @property
    def material(self):
        """Return material."""
        return self.public_key_gpg


class RsaVerificationKey2018(JwkVerificationMethod):
    """RsaVerificationKey2018 VerificationMethod."""

    type: Literal["RsaVerificationKey2018"]


class X25519KeyAgreementKey2019(Base58VerificationMethod):
    """X25519KeyAgreementKey2019 VerificationMethod."""

    type: Literal["X25519KeyAgreementKey2019"]


class SchnorrSecp256k1VerificationKey2019(JwkVerificationMethod):
    """SchnorrSecp256k1VerificationKey2019 VerificationMethod."""

    type: Literal["SchnorrSecp256k1VerificationKey2019"]


class EcdsaSecp256k1RecoveryMethod2020(JwkVerificationMethod):
    """EcdsaSecp256k1RecoveryMethod2020 VerificationMethod."""

    type: Literal["EcdsaSecp256k1RecoveryMethod2020"]


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
