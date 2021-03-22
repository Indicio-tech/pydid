"""DID Document deserialization options."""

from typing import Set, Type, Union

from voluptuous import ALLOW_EXTRA, All, Invalid, Schema, Switch

from ..did import DID
from ..validation import Into, Option
from .verification_method_options import VerificationMethodOptions

RELATIONSHIPS = (
    "authentication",
    "assertionMethod",
    "keyAgreement",
    "capabilityInvocation",
    "capabilityDelegation",
)


def _verification_methods(schema):
    return {
        "verificationMethod": [schema],
        **{
            key: [Switch(str, schema)]
            for key in (
                "authentication",
                "assertionMethod",
                "keyAgreement",
                "capabilityInvocation",
                "capabilityDelegation",
            )
        },
    }


def _options_of_type(type_: Type, options: Set[Option]):
    return filter(lambda option: isinstance(option, type_), options)


def _insert_missing_ids(value: dict):
    if "id" not in value:
        raise Invalid("No DID found in value.")

    did = DID(value["id"])
    index = 0

    def _walk(value: Union[str, list, dict]):
        nonlocal index
        if isinstance(value, str):
            return
        if isinstance(value, list):
            for item in value:
                _walk(item)
            return
        if isinstance(value, dict):
            if "id" not in value:
                value["id"] = str(did.ref("inserted-{}".format(index)))
                index += 1
                return

    for nested in value.values():
        _walk(nested)

    return value


class DIDDocumentOption(Option):
    """Container for validation options for DID Documents.

    Aggregates options of nested objects.
    """

    allow_public_key = 0, Schema(
        {Into("publicKey", "verificationMethod"): [dict]},
        extra=ALLOW_EXTRA,
    )
    insert_missing_ids = 1, Schema(_insert_missing_ids)

    @property
    def priority(self):
        return self.value[0]

    @property
    def schema(self):
        return self.value[1]

    @classmethod
    def apply(cls, value, options: Set[Option]):
        """Apply options to value."""
        # Apply DID Doc options
        doc_options = All(
            *cls.schemas_in_application_order(_options_of_type(cls, options))
        )
        value = doc_options(value)

        # Apply verification method options.
        vm_options = Schema(
            _verification_methods(
                All(
                    *cls.schemas_in_application_order(
                        _options_of_type(VerificationMethodOptions, options)
                    )
                )
            ),
            extra=ALLOW_EXTRA,
        )
        value = vm_options(value)
        return value
