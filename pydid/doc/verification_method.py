"""DID Doc Verification Method."""

from typing import Any, Set

from voluptuous import ALLOW_EXTRA, All, Coerce, Invalid, Remove, Schema, Union

from ..did import DID
from ..did_url import DIDUrl
from ..validation import Into, validate_init, wrap_validation_error
from . import DIDDocumentError
from .verification_method_options import VerificationMethodOptions


class InvalidVerificationMaterial(DIDDocumentError, Invalid):
    """Error raised when verification material is invalid."""


class VerificationMethodValidationError(DIDDocumentError):
    """Raised on VerificationMethod validation failure."""


def verification_material(value):
    """Validate Verification Material key."""
    if "publicKey" not in value:
        raise InvalidVerificationMaterial("Invalid")
    return value


class VerificationSuite:
    """
    Verification Suite of a Verification Method, defining type and material property.
    """

    def __init__(self, type_: str, verification_material_prop: str):
        """Initialize Suite.

        Args:
            type_ (str): type of the suite.
            verification_material_prop (str): property of the verification
                method map containing the key material.
        """
        self._type = type_
        self._verification_material_prop = verification_material_prop

    def __eq__(self, other):
        if not isinstance(other, VerificationSuite):
            return False
        return (
            self._type == other._type
            and self._verification_material_prop == other._verification_material_prop
        )

    @property
    def type(self):
        """Return type."""
        return self._type

    @property
    def verification_material_prop(self):
        """Return verification_material_prop."""
        return self._verification_material_prop

    @classmethod
    def derive(cls, type_: str, **potential_material_prop):
        """
        Derive the verification suite from a type string and a set of
        potential material properties.
        """
        for key in potential_material_prop:
            if "publicKey" in key:
                return cls(type_, key)
        raise InvalidVerificationMaterial(
            "the verification suite and material could not be derived from inputs"
        )


class VerificationMethod:
    """Representation of DID Document Verification Methods."""

    _validator = Schema(
        {
            "id": All(str, DIDUrl.validate),
            "type": str,
            "controller": All(str, DID.validate),
            All(str, verification_material): Union(str, dict),
        },
        required=True,
        extra=ALLOW_EXTRA,
    )

    @validate_init(id_=DIDUrl, suite=VerificationSuite, controller=DID)
    def __init__(
        self,
        id_: DIDUrl,
        suite: VerificationSuite,
        controller: DID,
        material: Any,
        **extra
    ):
        """Initialize VerificationMethod."""
        self._id = id_
        self._suite = suite
        self._controller = controller
        self._material = material
        self.extra = extra

    def __eq__(self, other):
        """Test equality."""
        if not isinstance(other, VerificationMethod):
            return False
        return (
            self._id == other._id
            and self._suite == other._suite
            and self._controller == other._controller
            and self._material == other._material
            and self.extra == other.extra
        )

    # pylint: disable=invalid-name
    @property
    def id(self):
        """Return id."""
        return self._id

    @property
    def suite(self):
        """Return suite."""
        return self._suite

    @property
    def type(self):
        """Return suite type."""
        return self._suite.type

    @property
    def controller(self):
        """Return controller."""
        return self._controller

    @property
    def material(self):
        """Return material."""
        return self._material

    def serialize(self):
        """Return serialized representation of VerificationMethod."""
        return {
            "id": str(self.id),
            "type": self.type,
            "controller": str(self.controller),
            self.suite.verification_material_prop: self.material,
            **self.extra,
        }

    @classmethod
    @wrap_validation_error(
        VerificationMethodValidationError,
        message="Failed to validate verification method",
    )
    def validate(cls, value: dict):
        """Validate against verification method."""
        return cls._validator(value)

    @classmethod
    @wrap_validation_error(
        VerificationMethodValidationError,
        message="Failed to deserialize verification method",
    )
    def deserialize(
        cls, value: dict, *, options: Set[VerificationMethodOptions] = None
    ):
        """Deserialize into VerificationMethod."""
        # Apply options
        if options:
            value = VerificationMethodOptions.apply(value, options)

        # Perform validation
        value = cls.validate(value)

        def _suite_and_material(value):
            suite = VerificationSuite.derive(value["type"], **value)
            material = value[suite.verification_material_prop]
            value["suite"] = suite
            value["material"] = material
            return value

        deserializer = Schema(
            All(
                {
                    Into("id", "id_"): All(str, DIDUrl.parse),
                    "controller": All(str, Coerce(DID)),
                },
                _suite_and_material,
                {Remove("type"): str, Remove(verification_material): Union(str, dict)},
            ),
            extra=ALLOW_EXTRA,
        )

        # Hydrate object
        value = deserializer(value)
        return cls(**value)
