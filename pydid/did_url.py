"""DID URL Object."""
from typing import Dict, Union
from urllib.parse import parse_qsl, urlencode, urlparse

from voluptuous import Invalid

from .common import DID_PATTERN, DIDError


class InvalidDIDUrlError(DIDError, Invalid):
    """Invalid DID."""


class DIDUrl:
    """DID URL."""

    def __init__(
        self,
        did: str,
        path: str = None,
        query: Dict[str, str] = None,
        fragment: Union[str, int] = None,
    ):
        """Initialize DID URL.

        Leading '/' of path inserted if absent.
        """
        self.did = did
        if path and not path.startswith("/"):
            path = "/" + path
        self.path = path

        self.query = query
        self.fragment = str(fragment) if fragment else None
        self.url = self._stringify()

    def _stringify(self):
        """Stringify DID URL from parts.

        Leading '/' of path inserted if absent.
        Delimiters for query and fragment will be inserted.
        """
        value = self.did
        if self.path:
            value += self.path

        if self.query:
            value += "?" + urlencode(self.query)

        if self.fragment:
            value += "#" + self.fragment

        return value

    def __str__(self):
        """Return string representation of DID URL.

        Delimiters for query and fragment will be inserted.
        """
        return self.url

    def __repr__(self):
        """Return debug representation of DID URL."""
        return "<DIDUrl {}>".format(self.url)

    def __eq__(self, other):
        """Check equality."""
        if isinstance(other, str):
            return self.url == other
        if not isinstance(other, DIDUrl):
            return False
        return self.url == other.url

    def __hash__(self):
        """Hash url string."""
        return hash(self.url)

    @classmethod
    def parse(cls, url: str):
        """Parse DID URL from string."""
        matches = DID_PATTERN.match(url)

        if not matches:
            raise InvalidDIDUrlError("DID could not be parsed from URL {}".format(url))

        did = matches.group(0)
        _, url_component = url.split(did)

        if not url_component:
            raise InvalidDIDUrlError(
                "No path, query, or fragment found in URL {}".format(url)
            )

        parts = urlparse(url_component)
        return cls(
            did,
            parts.path or None,
            dict(parse_qsl(parts.query)) if parts.query else None,
            parts.fragment or None,
        )

    @classmethod
    def as_str(
        cls,
        did: str,
        path: str = None,
        query: Dict[str, str] = None,
        fragment: str = None,
    ):
        """Form a DID URL from parts and return the string representation."""
        return str(cls(did, path, query, fragment))

    @classmethod
    def is_valid(cls, url: str):
        """Return whether the given string is a valid DID URL."""
        try:
            cls.parse(url)
        except InvalidDIDUrlError:
            return False
        else:
            return True

    @classmethod
    def validate(cls, url: str):
        """Validate the given url as a DID URL."""
        cls.parse(url)
        return url
