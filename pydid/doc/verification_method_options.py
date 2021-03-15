"""Additional validation options for Verification Methods."""

from typing import Union
from enum import Enum
from voluptuous import Schema, All, ALLOW_EXTRA
from ..did_url import DIDUrl


def _option_allow_type_list(value: Union[str, list]):
    """Provide mapping for allow type list option."""
    return value[0] if isinstance(value, list) else value


def _option_allow_controller_list(value: Union[str, list]):
    """Provide mapping for allwo controller list option."""
    return value[0] if isinstance(value, list) else value


def _option_allow_missing_controller(value: dict):
    """Derive controller value from id."""
    value["controller"] = DIDUrl.parse(value["id"]).did
    return value


class VerificationMethodOptions(Enum):
    """Container for validation options for VerificationMethods."""

    allow_type_list = 0, Schema(
        {"type": All([str], _option_allow_type_list)}, extra=ALLOW_EXTRA
    )
    allow_missing_controller = 1, Schema(
        All({"id": All(str, DIDUrl.validate)}, _option_allow_missing_controller),
        extra=ALLOW_EXTRA,
    )
    allow_controller_list = 2, Schema(
        {"controller": All([str], _option_allow_controller_list)}, extra=ALLOW_EXTRA
    )

    @property
    def priority(self):
        """Return the priority for this option."""
        return self.value[0]

    @property
    def mapper(self):
        """Return the mapper for this option. Alias to enum value."""
        return self.value[1]
