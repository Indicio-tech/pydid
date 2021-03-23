"""DID Document and resource builders."""

from contextlib import contextmanager
from typing import Any, List, Union, Iterator

from voluptuous import All, Coerce, Switch

from ..did import DID
from ..did_url import DIDUrl
from ..validation import validate_init
from .didcomm_service import DIDCommService
from .doc import DIDDocument
from .service import Service
from .verification_method import VerificationMethod, VerificationSuite
from .verification_relationship import VerificationRelationship


def _default_id_generator(base: str, start: int = 0) -> Iterator[str]:
    """Generate ID fragments."""
    index = start
    while True:
        yield "{}-{}".format(base, index)
        index += 1


class VerificationMethodBuilder:
    """VerificationMethod scoped builder."""

    def __init__(
        self, did: DID, *, id_base: str = None, methods: List[VerificationMethod] = None
    ):
        self._did = did
        self.methods = methods or []
        self._id_base = id_base or "keys"
        self._id_generator = None
        self._default_suite = None

    def _default_id_generator(self):
        """Default ID generator."""
        yield from _default_id_generator(self._id_base, start=len(self.methods))

    @contextmanager
    def defaults(
        self, id_generator: Iterator[str] = None, suite: VerificationSuite = None
    ) -> "VerificationMethodBuilder":
        """Enter context with defaults set."""
        self._id_generator = id_generator or self._default_id_generator()
        self._default_suite = suite
        try:
            yield self
        finally:
            self._id_generator = None
            self._default_suite = None

    def add(
        self,
        material: Any,
        suite: VerificationSuite = None,
        ident: str = None,
        controller: DID = None,
    ):
        """Add verification method from parts and context."""
        if not ident and not self._id_generator:
            raise ValueError("No ident provided for method")
        ident = ident or next(self._id_generator)
        suite = suite or self._default_suite
        if not suite:
            raise ValueError("No VerificationSuite or default suite")
        controller = controller or self._did
        vmethod = VerificationMethod(
            id_=self._did.ref(ident),
            suite=suite,
            controller=controller,
            material=material,
        )
        self.methods.append(vmethod)
        return vmethod

    def remove(self, vmethod: VerificationMethod):
        """Remove method from builder."""
        self.methods.remove(vmethod)


class RelationshipBuilder(VerificationMethodBuilder):
    """Builder for relationships."""

    def __init__(
        self, did: DID, id_base: str, *, methods: VerificationRelationship = None
    ):
        super().__init__(
            did, id_base=id_base, methods=methods.items if methods else None
        )

    def _default_id_generator(self):
        """Default ID generator."""
        start = len(
            [
                vmethod
                for vmethod in self.methods
                if isinstance(vmethod, VerificationMethod)
            ]
        )
        yield from _default_id_generator(self._id_base, start=start)

    @contextmanager
    def defaults(
        self, id_generator: Iterator[str] = None, suite: VerificationSuite = None
    ) -> "RelationshipBuilder":
        """Enter context with defaults set."""
        self._id_generator = id_generator or self._default_id_generator()
        self._default_suite = suite
        try:
            yield self
        finally:
            self._id_generator = None
            self._default_suite = None

    def reference(self, ref: DIDUrl):
        """Add reference to relationship."""
        if not isinstance(ref, DIDUrl):
            raise ValueError(
                "Reference must be DIDUrl, not {}".format(type(ref).__name__)
            )

        self.methods.append(ref)

    def embed(
        self,
        material: Any,
        suite: VerificationSuite = None,
        ident: str = None,
        controller: DID = None,
    ):
        """Embed verification method in relationship."""
        return super().add(material, suite, ident, controller)

    def remove(self, vmethod: Union[DIDUrl, VerificationMethod]):
        """Remove reference or method from builder."""
        self.methods.remove(vmethod)


class ServiceBuilder:
    """Builder for services."""

    def __init__(self, did: DID, *, services: List[Service] = None):
        self._did = did
        self.services = services or []
        self._id_generator = None

    @contextmanager
    def defaults(self, id_generator: Iterator[str] = None) -> "ServiceBuilder":
        """Enter context with defaults."""
        self._id_generator = id_generator or _default_id_generator(
            "service", start=len(self.services)
        )
        try:
            yield self
        finally:
            self._id_generator = None

    def add(self, type_: str, endpoint: str, ident: str = None, **extra):
        """Add service."""
        ident = ident or next(self._id_generator)
        service = Service(self._did.ref(ident), type_, endpoint, **extra)
        self.services.append(service)
        return service

    def add_didcomm(
        self,
        endpoint: str,
        recipient_keys: List[VerificationMethod],
        routing_keys: List[VerificationMethod] = None,
        *,
        type_: str = None,
        ident: str = None
    ):
        """Add DIDComm Service."""
        ident = ident or next(self._id_generator)
        recipient_keys = [vmethod.id for vmethod in recipient_keys]
        routing_keys = routing_keys or []
        routing_keys = [vmethod.id for vmethod in routing_keys]
        service = DIDCommService(
            self._did.ref(ident),
            endpoint,
            recipient_keys,
            routing_keys=routing_keys,
            type_=type_,
        )
        self.services.append(service)
        return service

    def remove(self, service: Service):
        """Remove service from builder."""
        self.services.remove(service)


class DIDDocumentBuilder:
    """Builder for constructing DID Documents programmatically."""

    DEFAULT_CONTEXT = ["https://www.w3.org/ns/did/v1"]

    @validate_init(id_=Switch(All(str, Coerce(DID)), DID))
    def __init__(
        self,
        id_: Union[str, DID],
        context: List[str] = None,
        *,
        also_known_as: List[str] = None,
        controller: List[str] = None
    ):
        """Initliaze builder."""
        self.id = id_
        self.context = context or self.DEFAULT_CONTEXT
        self.also_known_as = also_known_as
        self.controller = controller
        self.verification_methods = VerificationMethodBuilder(self.id)
        self.authentication = RelationshipBuilder(self.id, "auth")
        self.assertion_method = RelationshipBuilder(self.id, "assert")
        self.key_agreement = RelationshipBuilder(self.id, "key-agreement")
        self.capability_invocation = RelationshipBuilder(
            self.id, "capability-invocation"
        )
        self.capability_delegation = RelationshipBuilder(
            self.id, "capability-delegation"
        )
        self.services = ServiceBuilder(self.id)
        self.extra = {}

    @classmethod
    def from_doc(cls, doc: DIDDocument) -> "DIDDocumentBuilder":
        """Create a Builder from an existing DIDDocument."""
        builder = cls(
            id_=doc.id,
            context=doc.context,
            also_known_as=doc.also_known_as,
            controller=doc.controller,
        )
        builder.verification_methods = VerificationMethodBuilder(
            doc.id, methods=doc.verification_method
        )
        builder.authentication = RelationshipBuilder(
            doc.id, "auth", methods=doc.authentication
        )
        builder.assertion_method = RelationshipBuilder(
            doc.id, "assert", methods=doc.assertion_method
        )
        builder.key_agreement = RelationshipBuilder(
            doc.id, "key-agreement", methods=doc.key_agreement
        )
        builder.capability_invocation = RelationshipBuilder(
            doc.id, "capability-invocation", methods=doc.capability_invocation
        )
        builder.capability_delegation = RelationshipBuilder(
            doc.id, "capability-delegation", methods=doc.capability_delegation
        )
        builder.services = ServiceBuilder(doc.id, services=doc.service)
        return builder

    def build(self) -> DIDDocument:
        """Build document."""
        return DIDDocument(
            id=self.id,
            context=self.context,
            also_known_as=self.also_known_as,
            controller=self.controller,
            verification_method=self.verification_methods.methods or None,
            authentication=VerificationRelationship(self.authentication.methods)
            or None,
            assertion_method=VerificationRelationship(self.assertion_method.methods)
            or None,
            key_agreement=VerificationRelationship(self.key_agreement.methods) or None,
            capability_invocation=VerificationRelationship(
                self.capability_invocation.methods
            )
            or None,
            capability_delegation=VerificationRelationship(
                self.capability_delegation.methods
            )
            or None,
            service=self.services.services or None,
            **self.extra
        )
