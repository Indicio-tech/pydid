"""DID Document deserialization options."""

from typing import Set, Type

from voluptuous import Schema, All, ALLOW_EXTRA, Union

from .verification_method import VerificationMethod
from .verification_method_options import VerificationMethodOptions
from ..validation import Into, Option


def _verification_methods(schema):
    return {
        "verificationMethod": [schema],
        **{
            key: [Union(str, schema)]
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


class DIDDocumentOption(Option):
    """Container for validation options for DID Documents.

    Aggregates options of nested objects.
    """

    allow_public_key = 0, Schema(
        {Into("publicKey", "verificationMethod"): [VerificationMethod.validate]},
        extra=ALLOW_EXTRA,
    )

    @property
    def priority(self):
        return self.value[0]

    @property
    def schema(self):
        return self.value[1]

    @classmethod
    def apply(cls, value, options: Set[Option]):
        """Apply options to value."""
        # Apply verification method options.
        vm_options = Schema(
            _verification_methods(
                All(
                    *cls.schemas_in_application_order(
                        _options_of_type(VerificationMethodOptions, options)
                    )
                )
            )
        )
        value = vm_options(value)

        # Apply DID Doc options
        doc_options = All(
            *cls.schemas_in_application_order(_options_of_type(cls, options))
        )
        value = doc_options(value)
        return value
