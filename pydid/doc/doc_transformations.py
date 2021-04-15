"""DID Document deserialization options."""

from enum import Enum
from typing import Union

from voluptuous import ALLOW_EXTRA, Invalid, Schema

from ..did import DID
from ..validation import Into


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


class DIDDocumentTransformations(Enum):
    """Container for validation options for DID Documents.

    Aggregates options of nested objects.
    """

    allow_public_key = Schema(
        {Into("publicKey", "verificationMethod"): [dict]},
        extra=ALLOW_EXTRA,
    )
    insert_missing_ids = Schema(_insert_missing_ids)

    def __call__(self, value):
        """Call the schema."""
        return self.value(value)
