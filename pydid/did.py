"""W3C DID Representation.

DID Parsing rules derived from W3C Decentrialized Identifiers v1.0 Working Draft 18
January 2021:

    https://w3c.github.io/did-core/

"""

from typing import Dict, Optional

from .common import DID_PATTERN, DIDError
from .did_url import DIDUrl


class InvalidDIDError(DIDError, ValueError):
    """Invalid DID."""


class DID(str):
    """DID Representation and helpers."""

    def __init__(self, did: str):
        """Validate and parse raw DID str."""
        super().__init__()
        if isinstance(did, DID):
            self._method = did.method
            self._id = did._id
            return

        matched = DID_PATTERN.match(did)
        if not matched:
            raise InvalidDIDError("Unable to parse DID {}".format(did))
        self._method = matched.group(1)
        self._id = matched.group(2)

    @classmethod
    def __get_validators__(cls):
        """Yield validators for pydantic."""
        yield cls._validate

    @classmethod
    def __modify_schema__(cls, field_schema):  # pragma: no cover
        """Update schema fields."""
        field_schema.update(pattern=DID_PATTERN)

    @property
    def method(self):
        """Return the method of this DID."""
        return self._method

    @property
    def method_specific_id(self):
        """Return the method specific identifier."""
        return self._id

    def url(
        self,
        path: Optional[str] = None,
        query: Optional[Dict[str, str]] = None,
        fragment: Optional[str] = None,
    ):
        """Return a DID URL for this DID."""
        return DIDUrl.unparse(self, path, query, fragment)

    def ref(self, ident: str) -> DIDUrl:
        """Return a DID reference (URL) for use as an ID in a DID Doc section."""
        return DIDUrl.unparse(self, fragment=ident)

    @classmethod
    def is_valid(cls, did: str):
        """Return if the passed string is a valid DID."""
        return DID_PATTERN.match(did)

    @classmethod
    def validate(cls, did: str):
        """Validate the given string as a DID."""
        if not cls.is_valid(did):
            raise InvalidDIDError('"{}" is not a valid DID'.format(did))
        return did

    @classmethod
    def _validate(cls, did):
        """Pydantic validator."""
        return cls(did)
