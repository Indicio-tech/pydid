"""DID Document and resource builders."""

from contextlib import contextmanager
from typing import Any, ContextManager, Iterable, List, Union

from voluptuous import All, Coerce, Switch

from ..did import DID
from ..did_url import DIDUrl
from ..validation import validate_init
from .didcomm_service import DIDCommService
from .doc import DIDDocument
from .service import Service
from .verification_method import VerificationMethod, VerificationSuite
from .verification_relationship import VerificationRelationship


class VerificationMethodBuilder:
    """VerificationMethod scoped builder."""

    def __init__(
        self,
        did: DID,
        id_generator: Iterable[str],
        default_suite: VerificationSuite = None,
    ):
        self.did = did
        self.methods = []
        self.id_generator = id_generator
        self.default_suite = default_suite

    def add(
        self,
        material: Any,
        suite: VerificationSuite = None,
        ident: str = None,
        controller: DID = None,
    ):
        """Add verification method from parts and context."""
        ident = ident or next(self.id_generator)
        controller = controller or self.did
        suite = suite or self.default_suite
        if not suite:
            raise ValueError("No VerificationSuite or default suite")
        vmethod = VerificationMethod(
            id_=self.did.ref(ident),
            suite=suite,
            controller=controller,
            material=material,
        )
        self.methods.append(vmethod)
        return vmethod


class RelationshipBuilder:
    """Builder for relationships."""

    def __init__(
        self,
        did: DID,
        id_generator: Iterable[str],
        default_suite: VerificationSuite = None,
    ):
        self.did = did
        self.methods = []
        self.id_generator = id_generator
        self.default_suite = default_suite
        self.method_builder = VerificationMethodBuilder(
            did, id_generator, default_suite
        )

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
        """Add verification method from parts and context."""
        vmethod = self.method_builder.add(material, suite, ident, controller)
        self.methods.append(vmethod)
        return vmethod


class ServiceBuilder:
    """Builder for services."""

    def __init__(
        self,
        did: DID,
        id_generator: Iterable[str],
    ):
        self.did = did
        self.id_generator = id_generator
        self.services = []

    def add(self, type_: str, endpoint: str, ident: str = None, **extra):
        """Add service."""
        ident = ident or next(self.id_generator)
        service = Service(self.did.ref(ident), type_, endpoint, **extra)
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
        ident = ident or next(self.id_generator)
        recipient_keys = [vmethod.id for vmethod in recipient_keys]
        routing_keys = routing_keys or []
        routing_keys = [vmethod.id for vmethod in routing_keys]
        service = DIDCommService(
            self.did.ref(ident),
            endpoint,
            recipient_keys,
            routing_keys=routing_keys,
            type_=type_,
        )
        self.services.append(service)
        return service


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
        self._verification_methods = []
        self._authentication = VerificationRelationship([])
        self._assertion_method = VerificationRelationship([])
        self._key_agreement = VerificationRelationship([])
        self._capability_invocation = VerificationRelationship([])
        self._capability_delegation = VerificationRelationship([])
        self._services = []

    @classmethod
    def from_doc(cls, doc: DIDDocument) -> "DIDDocumentBuilder":
        """Create a Builder from an existing DIDDocument."""
        builder = cls(
            id_=doc.id,
            context=doc.context,
            also_known_as=doc.also_known_as,
            controller=doc.controller,
        )
        builder._verification_methods = doc.verification_method
        builder._authentication = doc.authentication or VerificationRelationship([])
        builder._assertion_method = doc.assertion_method or VerificationRelationship([])
        builder._key_agreement = doc.key_agreement or VerificationRelationship([])
        builder._capability_invocation = (
            doc.capability_invocation or VerificationRelationship([])
        )
        builder._capability_delegation = (
            doc.capability_delegation or VerificationRelationship([])
        )
        builder._services = doc.service
        return builder

    @staticmethod
    def _default_id_generator(base: str, start: int = 0) -> Iterable[str]:
        """Generate ID fragments."""
        index = start
        while True:
            yield "{}-{}".format(base, index)
            index += 1

    @contextmanager
    def verification_methods(
        self,
        id_generator: Iterable[str] = None,
        default_suite: VerificationSuite = None,
    ) -> ContextManager[VerificationMethodBuilder]:
        """Builder for verification methods."""
        subbuilder = VerificationMethodBuilder(
            self.id,
            id_generator
            or self._default_id_generator(
                "keys", start=len(self._verification_methods)
            ),
            default_suite,
        )
        yield subbuilder
        self._verification_methods.extend(subbuilder.methods)

    @contextmanager
    def _relationship(
        self,
        relationship: VerificationRelationship,
        ident_base: str = None,
        id_generator: Iterable[str] = None,
        default_suite: VerificationSuite = None,
    ) -> ContextManager[RelationshipBuilder]:
        """Builder for relationships."""
        start = len(relationship.items)
        subbuilder = RelationshipBuilder(
            self.id,
            id_generator or self._default_id_generator(ident_base, start),
            default_suite,
        )
        yield subbuilder
        relationship.items.extend(subbuilder.methods)

    @contextmanager
    def authentication(
        self,
        id_generator: Iterable[str] = None,
        default_suite: VerificationSuite = None,
    ) -> ContextManager[RelationshipBuilder]:
        """Builder for authentication relationship."""
        with self._relationship(
            self._authentication, "auth", id_generator, default_suite
        ) as builder:
            yield builder

    @contextmanager
    def assertion_method(
        self,
        id_generator: Iterable[str] = None,
        default_suite: VerificationSuite = None,
    ) -> ContextManager[RelationshipBuilder]:
        """Builder for assertion_method relationship."""
        with self._relationship(
            self._assertion_method, "assert", id_generator, default_suite
        ) as builder:
            yield builder

    @contextmanager
    def key_agreement(
        self,
        id_generator: Iterable[str] = None,
        default_suite: VerificationSuite = None,
    ) -> ContextManager[RelationshipBuilder]:
        """Builder for key_agreement relationship."""
        with self._relationship(
            self._key_agreement, "key-agreement", id_generator, default_suite
        ) as builder:
            yield builder

    @contextmanager
    def capability_invocation(
        self,
        id_generator: Iterable[str] = None,
        default_suite: VerificationSuite = None,
    ) -> ContextManager[RelationshipBuilder]:
        """Builder for capability_invocation relationship."""
        with self._relationship(
            self._capability_invocation,
            "capability-invocation",
            id_generator,
            default_suite,
        ) as builder:
            yield builder

    @contextmanager
    def capability_delegation(
        self,
        id_generator: Iterable[str] = None,
        default_suite: VerificationSuite = None,
    ) -> ContextManager[RelationshipBuilder]:
        """Builder for capability_delegation relationship."""
        with self._relationship(
            self._capability_delegation,
            "capability-delegation",
            id_generator,
            default_suite,
        ) as builder:
            yield builder

    @contextmanager
    def services(
        self, id_generator: Iterable[str] = None
    ) -> ContextManager[ServiceBuilder]:
        """Builder for services."""
        id_generator = id_generator or self._default_id_generator(
            "service", start=len(self._services)
        )
        subbuilder = ServiceBuilder(self.id, id_generator)
        yield subbuilder
        self._services.extend(subbuilder.services)

    def build(self) -> DIDDocument:
        """Build document."""
        return DIDDocument(
            id=self.id,
            context=self.context,
            also_known_as=self.also_known_as,
            controller=self.controller,
            verification_method=self._verification_methods or None,
            authentication=self._authentication or None,
            assertion_method=self._assertion_method or None,
            key_agreement=self._key_agreement or None,
            capability_invocation=self._capability_invocation or None,
            capability_delegation=self._capability_delegation or None,
            service=self._services or None,
        )
