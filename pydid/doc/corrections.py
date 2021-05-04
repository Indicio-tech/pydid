"""DID Document deserialization options."""

from typing import Union

from ..did import DID


def insert_missing_ids(value: dict):
    """Insert missing resource IDs.

    This correction can be applied using the coerce decorator on your Document class:

    >>> from pydid.validation import coerce
    >>> from pydid.doc import DIDDocument
    >>> @coerce([insert_missing_ids])
    >>> class MyDIDDocument(DIDDocument):
    >>>     '''My cool DID Document.'''
    >>>     # Other attributes...

    Or by decorating an existing class:
    >>> from pydid.validation import coerce
    >>> from pydid.doc import DIDDocument
    >>> MyDIDDocument = coerce([insert_missing_ids])(DIDDocument)
    """
    if "id" not in value:
        raise ValueError("No ID found in Document.")

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
