"""W3C DID Representation.

DID Parsing rules derived from W3C Decentrialized Identifiers v1.0 Working Draft 18
January 2021:

    https://w3c.github.io/did-core/

"""

from typing import Dict

from voluptuous import Invalid

from .common import DID_PATTERN, DIDError
from .did_url import DIDUrl


class InvalidDIDError(DIDError, Invalid):
    """Invalid DID."""


class DID:
    """DID Representation and helpers."""

    def __init__(self, did: str):
        """Validate and parse raw DID str."""
        self._raw = did
        matched = DID_PATTERN.fullmatch(did)
        if not matched:
            raise InvalidDIDError("Unable to parse DID {}".format(did))
        self._method = matched.group(1)
        self._id = matched.group(2)

    @property
    def method(self):
        """Return the method of this DID."""
        return self._method

    @property
    def method_specific_id(self):
        """Return the method specific identifier."""
        return self._id

    def __str__(self):
        """Return string representation of DID."""
        return self._raw

    def __repr__(self):
        """Return debug representation of DID."""
        return "<DID {}>".format(self._raw)

    def __eq__(self, other):
        """Test equality."""
        if isinstance(other, str):
            return self._raw == other
        if isinstance(other, DID):
            return self._raw == other._raw

        return False

    def __hash__(self):
        """Return hash."""
        return hash(self._raw)

    def url(self, path: str = None, query: Dict[str, str] = None, fragment: str = None):
        """Return a DID URL for this DID."""
        return DIDUrl(self._raw, path, query, fragment)

    def ref(self, ident: str) -> DIDUrl:
        """Return a DID reference (URL) for use as an ID in a DID Doc section."""
        return DIDUrl(self._raw, fragment=ident)

    @classmethod
    def is_valid(cls, did: str):
        """Return if the passed string is a valid DID."""
        return DID_PATTERN.fullmatch(did)

    @classmethod
    def validate(cls, did: str):
        """Validate the given string as a DID."""
        if not cls.is_valid(did):
            raise InvalidDIDError('"{}" is not a valid DID'.format(did))
        return did
