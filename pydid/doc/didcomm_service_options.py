"""Additional validation options for Services."""

from typing import Set

from voluptuous import ALLOW_EXTRA, All, Schema, Switch, Required

from ..validation import Option


def _option_allow_empty_endpoints(value: str):
    """allow empty service endpoint value."""

    return value


class ServicesMethodsOptions(Option):
    """Container for validation options for did comm services."""

    allow_empty_endpoints = 0, Schema(
        All(
            {"serviceEndpoint": All(str)},
            _option_allow_empty_endpoints,
        ),
        extra=ALLOW_EXTRA,
    )

    @property
    def priority(self):
        """Return the priority for this option."""
        return self.value[0]

    @property
    def schema(self):
        """Return the schema defined by option."""
        return self.value[1]

    @classmethod
    def apply(cls, value, options: Set["ServicesMethodsOptions"]):
        """Apply options to value"""
        return All(*cls.schemas_in_application_order(options))(value)
