"""Additional validation options for Verification Methods."""

from enum import Enum
from typing import Union

from voluptuous import ALLOW_EXTRA, All, Schema, Switch, Required

from ..did_url import DIDUrl


RELATIONSHIPS = (
    "authentication",
    "assertionMethod",
    "keyAgreement",
    "capabilityInvocation",
    "capabilityDelegation",
)


def _verification_methods(schema):
    return Schema(
        {
            "verificationMethod": [schema],
            **{key: [Switch(str, schema)] for key in RELATIONSHIPS},
        },
        extra=ALLOW_EXTRA,
    )


def _option_allow_type_list(value: Union[str, list]):
    """Provide mapping for allow type list option."""
    return value[0] if isinstance(value, list) else value


def _option_allow_controller_list(value: Union[str, list]):
    """Provide mapping for allow controller list option."""
    return value[0] if isinstance(value, list) else value


def _option_allow_missing_controller(value: dict):
    """Derive controller value from id."""
    if "controller" not in value:
        value["controller"] = DIDUrl.parse(value["id"]).did
    return value


class VerificationMethodTransformations(Enum):
    """Container for validation options for VerificationMethods."""

    allow_type_list = Schema(
        {"type": All(Switch(str, [str]), _option_allow_type_list)}, extra=ALLOW_EXTRA
    )
    allow_missing_controller = Schema(
        All(
            {Required("id"): All(str, DIDUrl.validate)},
            _option_allow_missing_controller,
        ),
        extra=ALLOW_EXTRA,
    )
    allow_controller_list = Schema(
        {"controller": All(Switch(str, [str]), _option_allow_controller_list)},
        extra=ALLOW_EXTRA,
    )

    def __call__(self, value):
        """Call transform option."""
        return _verification_methods(self.value)(value)
