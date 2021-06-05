"""DID URL Object."""
from typing import Dict, Optional, TYPE_CHECKING
from urllib.parse import parse_qsl, urlencode, urlparse

from .common import DID_URL_DID_PART_PATTERN, DIDError, DID_URL_RELATIVE_FRONT

if TYPE_CHECKING:  # pragma: no cover
    from .did import DID


class InvalidDIDUrlError(DIDError, ValueError):
    """Invalid DID."""


class DIDUrl(str):
    """DID URL."""

    def __init__(self, url: str):
        """Parse DID URL from string."""
        super().__init__()
        matches = DID_URL_DID_PART_PATTERN.match(url)

        if matches:
            self.did = matches.group(1)
            _, url_component = url.split(self.did)
        else:
            relative_matches = DID_URL_RELATIVE_FRONT.match(url)
            if not relative_matches:
                raise InvalidDIDUrlError(
                    "{} is not a valid absolute or relative DID URL".format(url)
                )
            self.did = None
            url_component = url

        parts = urlparse(url_component)
        self.path = parts.path or None
        self.query = dict(parse_qsl(parts.query)) if parts.query else None
        self.fragment = parts.fragment or None

    @classmethod
    def __get_validators__(cls):
        """Yield validators."""
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):  # pragma: no cover
        """Update schema fields."""
        field_schema.update(examples=["did:example:123/some/path?query=test#fragment"])

    @classmethod
    def parse(cls, url: str):
        """Parse DID URL from string."""
        return cls(url)

    @classmethod
    def unparse(
        cls,
        did: str,
        path: Optional[str] = None,
        query: Optional[Dict[str, str]] = None,
        fragment: Optional[str] = None,
    ) -> "DIDUrl":
        """Form a DID URL from parts and return the string representation."""
        value = did
        if path and not path.startswith("/"):
            path = "/" + path

        if path:
            value += path

        if query:
            value += "?" + urlencode(query)

        fragment = str(fragment) if fragment else None
        if fragment:
            value += "#" + fragment

        return cls(value)

    def as_absolute(self, did: "DID"):
        """Make a relative DIDUrl absolute."""
        return self.unparse(did, self.path, self.query, self.fragment)

    @classmethod
    def is_valid(cls, url: str):
        """Return whether the given string is a valid DID URL."""
        try:
            cls.validate(url)
        except ValueError:
            return False
        else:
            return True

    @classmethod
    def validate(cls, url: str):
        """Validate the given url as a DID URL."""
        return cls.parse(url)
