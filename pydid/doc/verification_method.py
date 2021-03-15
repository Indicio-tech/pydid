"""DID Doc Verification Method."""

from typing import Any, Set
from voluptuous import Schema, All, Invalid, Union
from ..did import DID
from ..did_url import DIDUrl
from . import DIDDocError
from .verification_method_options import VerificationMethodOptions

allow_type_list = VerificationMethodOptions.allow_type_list
allow_controller_list = VerificationMethodOptions.allow_controller_list
allow_missing_controller = VerificationMethodOptions.allow_missing_controller

__all__ = [
    "VerificationSuite",
    "VerificationMethod",
    "allow_type_list",
    "allow_controller_list",
    "allow_missing_controller",
]


class InvalidVerificationMaterial(DIDDocError, Invalid):
    """Error raised when verification material is invalid."""


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

    validate = Schema(
        {
            "id": All(str, DIDUrl.validate),
            "type": str,
            "controller": All(str, DID.validate),
            All(str, verification_material): Union(str, dict),
        },
        required=True,
    )

    def __init__(
        self, id_: DIDUrl, suite: VerificationSuite, controller: DIDUrl, material: Any
    ):
        """Initialize VerificationMethod."""
        self._id = id_
        self._suite = suite
        self._controller = controller
        self._material = material

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
            "id": self.id,
            "type": self.type,
            "controller": self.controller,
            self.suite.verification_material_prop: self.material,
        }

    @classmethod
    def deserialize(
        cls, value: dict, *, options: Set[VerificationMethodOptions] = None
    ):
        """Deserialize into VerificationMethod."""
        # Apply options
        if options:
            for option in sorted(options, key=lambda item: item.priority):
                value = option.mapper(value)

        # Perform validation
        value = cls.validate(value)

        # Hydrate object
        suite = VerificationSuite.derive(value["type"], **value)
        material = value[suite.verification_material_prop]
        return cls(
            id_=value["id"],
            controller=value["controller"],
            suite=suite,
            material=material,
        )
