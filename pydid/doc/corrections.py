"""Common DID Document corrections."""

from typing import Union

from ..did import DID


def insert_missing_ids(value: dict) -> dict:
    """Insert missing resource IDs.

    This correction can be applied directly to a raw document dictionary or
    with the pydid.deserialize_document method:

    >>> import pydid
    >>> doc_raw = {"@context": "http://example.com", "id": "did:example:123"}
    >>> doc_raw = pydid.corrections.insert_missing_ids(doc_raw)

    Or:
    >>> import pydid
    >>> doc_raw = {"@context": "http://example.com", "id": "did:example:123"}
    >>> doc = pydid.deserialize_document(
    ...     doc_raw, corrections=[pydid.corrections.insert_missing_ids]
    ... )
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


def public_key_is_verification_method(value: dict) -> dict:
    """Transform publicKey to verificationMethod.

    This is helpful if dealing with DID resolvers that have not updated to the
    latest DID Spec.

    This correction can be applied directly to a raw document dictionary or
    with the pydid.deserialize_document method:

    >>> import pydid
    >>> doc_raw = {
    ...     "@context": "http://example.com",
    ...     "id": "did:example:123",
    ...     "publicKey": [{"id": "did:example:123#key-1"}],
    ... }
    >>> doc_raw = pydid.corrections.public_key_is_verification_method(doc_raw)
    >>> assert "verificationMethod" in doc_raw
    >>> assert "publicKey" not in doc_raw

    Or:
    >>> import pydid
    >>> doc_raw = {
    ...     "@context": "http://example.com",
    ...     "id": "did:example:123",
    ...     "publicKey": [{"id": "did:example:123#key-1"}],
    ... }
    >>> doc = pydid.deserialize_document(
    ...     doc_raw, corrections=[pydid.corrections.public_key_is_verification_method]
    ... )
    >>> assert doc.verification_method
    """

    if "publicKey" in value:
        value["verificationMethod"] = value.pop("publicKey")
    return value
