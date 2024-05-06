"""DID Doc Verification Method."""

from typing import ClassVar, Optional, Set, Type, Union

from inflection import underscore
from pydantic import create_model, field_validator, model_validator, alias_generators
from typing_extensions import Literal

from pydid.validation import required_group

from .did import DID
from .did_url import DIDUrl, InvalidDIDUrlError
from .resource import Resource

set_of_material_properties = {
    "blockchain_account_id",
    "ethereum_address",
    "public_key_base58",
    "public_key_gpg",
    "public_key_hex",
    "public_key_jwk",
    "public_key_pem",
    "public_key_multibase",
}
material_properties_camel = {
    alias_generators.to_camel(prop) for prop in set_of_material_properties
}


class VerificationMaterial:
    """Type annotation marker for the material attribute of a verification method."""


class VerificationMaterialUnknown(NotImplementedError):
    """Raised when verification material is unknown but access is attempted."""


class VerificationMethod(Resource):
    """Representation of DID Document Verification Methods."""

    material_properties: ClassVar[Set[str]] = set_of_material_properties

    id: DIDUrl
    type: str
    controller: DID
    public_key_hex: Optional[str] = None
    public_key_base58: Optional[str] = None
    public_key_pem: Optional[str] = None
    public_key_multibase: Optional[str] = None
    blockchain_account_id: Optional[str] = None
    ethereum_address: Optional[str] = None
    public_key_jwk: Optional[dict] = None
    _material_prop: Optional[str] = None

    def __init__(self, **data):
        """Initialize a VerificationMethod."""
        super().__init__(**data)
        self._material_prop = self._material_prop or self._infer_material_prop()

    @classmethod
    def suite(cls: Type, typ: str, material: str, material_type: Type):
        """Return a subclass of VerificationMethod for a given type."""
        model = create_model(
            typ,
            __module__=cls.__module__,
            __base__=cls,
            type=(Literal[typ], ...),  # type:ignore
            **{underscore(material): (material_type, ...)},
        )
        model.material = property(
            lambda self: getattr(self, underscore(material)),
            lambda self, value: setattr(self, underscore(material), value),
        )
        model._material_prop = underscore(material)
        return model

    @field_validator("type", mode="before")
    @classmethod
    def _allow_type_list(cls, value: Union[str, list[str]]) -> str:
        """Unwrap type list.

        This validator handles a common DID Document mutation.
        """
        if isinstance(value, list):
            return value[0]
        return value

    @field_validator("controller", mode="before")
    @classmethod
    def _allow_controller_list(cls, value: Union[DID, list[DID]]) -> DID:
        """Unwrap controller list.

        This validator handles a common DID Document mutation.
        """
        if isinstance(value, list):
            return value[0]
        return value

    @model_validator(mode="before")
    @classmethod
    def _allow_missing_controller(cls, values: Union[dict, "VerificationMethod"]):
        """Derive controller value from ID.

        This validator handles a common DID Document mutation.
        """
        if not isinstance(values, dict):
            values = values.__dict__

        if "controller" not in values:
            if "id" not in values:
                raise ValueError(
                    "Could not derive controller: no id present in verification method"
                )
            try:
                ident = DIDUrl.parse(values["id"])
                values["controller"] = ident.did
            except InvalidDIDUrlError:
                pass
        return values

    @model_validator(mode="before")
    @classmethod
    def _method_appears_to_contain_material(
        cls, values: Union[dict, "VerificationMethod"]
    ):
        """Validate that the method appears to contain verification material."""
        if not isinstance(values, dict):
            values = values.__dict__

        if values.get("controller") and len(values) < 4:
            raise ValueError(
                "Key material expected, found: {}".format(list(values.keys()))
            )
        return values

    @model_validator(mode="before")
    @classmethod
    def _no_more_than_one_material_prop(cls, values: Union[dict, "VerificationMethod"]):
        """Validate that exactly one material property was specified on method."""
        if not isinstance(values, dict):
            values = values.__dict__

        model_properties = {key for key, value in values.items() if value is not None}

        set_material_properties = set_of_material_properties & model_properties
        set_material_properties_camel = material_properties_camel & model_properties

        if len(set_material_properties | set_material_properties_camel) > 1:
            raise ValueError(
                "Found properties {}; only one is allowed".format(
                    ", ".join(set_material_properties)
                )
            )
        return values

    def _infer_material_prop(self) -> Optional[str]:
        """Guess the property that appears to be the verification material.

        Guess is based on known material property names.
        """

        for prop, value in self:
            if prop in self.material_properties and value is not None:
                return prop

        return None

    @property
    def material(self):
        """Return material."""
        if not self._material_prop:
            raise VerificationMaterialUnknown(
                "Verification Material is not known for this method"
            )
        return getattr(self, self._material_prop)

    @classmethod
    def method_type(cls) -> Optional[str]:
        """Return method type if known."""
        return cls._fill_in_required_literals().get("type")


# Verification Method Suites registered in DID Spec


class Ed25519VerificationKey2018(VerificationMethod):
    """Ed25519VerificationKey2018 VerificationMethod."""

    type: Literal["Ed25519VerificationKey2018"]
    public_key_base58: str


class Ed25519VerificationKey2020(VerificationMethod):
    """Ed25519VerificationKey2020 VerificationMethod."""

    type: Literal["Ed25519VerificationKey2020"]
    public_key_multibase: str


class OpenPgpVerificationKey2019(VerificationMethod):
    """OpenPgpVerificationKey2019 VerificationMethod."""

    type: Literal["OpenPgpVerificationKey2019"]
    public_key_pem: str


class JsonWebKey2020(VerificationMethod):
    """JsonWebKey2020 VerificationMethod."""

    type: Literal["JsonWebKey2020"]
    public_key_jwk: dict


class EcdsaSecp256k1VerificationKey2019(VerificationMethod):
    """EcdsaSecp256k1VerificationKey2019 VerificationMethod."""

    type: Literal["EcdsaSecp256k1VerificationKey2019"]
    _require_one_of = required_group({"public_key_jwk", "public_key_hex"})


class Bls1238G1Key2020(VerificationMethod):
    """Bls1238G1Key2020 VerificationMethod."""

    type: Literal["Bls1238G1Key2020"]
    public_key_base58: str


class Bls1238G2Key2020(VerificationMethod):
    """Bls1238G2Key2020 VerificationMethod."""

    type: Literal["Bls1238G2Key2020"]
    public_key_base58: str


class GpgVerificationKey2020(VerificationMethod):
    """GpgVerificationKey2020 VerificationMethod."""

    type: Literal["GpgVerificationKey2020"]
    public_key_gpg: str


class RsaVerificationKey2018(VerificationMethod):
    """RsaVerificationKey2018 VerificationMethod."""

    type: Literal["RsaVerificationKey2018"]
    public_key_jwk: dict


class X25519KeyAgreementKey2019(VerificationMethod):
    """X25519KeyAgreementKey2019 VerificationMethod."""

    type: Literal["X25519KeyAgreementKey2019"]
    public_key_base58: str


class X25519KeyAgreementKey2020(VerificationMethod):
    """X25519KeyAgreementKey2020 VerificationMethod."""

    type: Literal["X25519KeyAgreementKey2020"]
    public_key_multibase: str


class SchnorrSecp256k1VerificationKey2019(VerificationMethod):
    """SchnorrSecp256k1VerificationKey2019 VerificationMethod."""

    type: Literal["SchnorrSecp256k1VerificationKey2019"]


class EcdsaSecp256k1RecoveryMethod2020(VerificationMethod):
    """EcdsaSecp256k1RecoveryMethod2020 VerificationMethod."""

    type: Literal["EcdsaSecp256k1RecoveryMethod2020"]
    _require_one_of = required_group(
        {"public_key_jwk", "public_key_hex", "ethereum_address"}
    )


class Multikey(VerificationMethod):
    """Multikey VerificationMethod."""

    type: Literal["Multikey"]
    public_key_multibase: str


class UnsupportedVerificationMethod(VerificationMethod):
    """Model representing unsupported verification methods."""


class UnknownVerificationMethod(VerificationMethod):
    """Model representing unknown verification methods."""


KnownVerificationMethods = Union[
    Ed25519VerificationKey2018,
    Ed25519VerificationKey2020,
    OpenPgpVerificationKey2019,
    JsonWebKey2020,
    EcdsaSecp256k1VerificationKey2019,
    Bls1238G1Key2020,
    Bls1238G2Key2020,
    GpgVerificationKey2020,
    RsaVerificationKey2018,
    X25519KeyAgreementKey2019,
    X25519KeyAgreementKey2020,
    SchnorrSecp256k1VerificationKey2019,
    EcdsaSecp256k1RecoveryMethod2020,
    Multikey,
]
