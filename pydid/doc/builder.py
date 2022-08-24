"""DID Document and resource builders."""

from typing import Iterator, List, Optional, Type, Union

from ..did import DID
from ..did_url import DIDUrl
from ..service import DIDCommService, Service
from ..verification_method import VerificationMethod
from .doc import DIDDocument


def _default_id_generator(base: str, start: int = 0) -> Iterator[str]:
    """Generate ID fragments."""
    index = start
    while True:
        yield "{}-{}".format(base, index)
        index += 1


class VerificationMethodBuilder:
    """VerificationMethod scoped builder."""

    def __init__(
        self,
        did: DID,
        *,
        id_base: str = None,
        methods: Optional[List[VerificationMethod]] = None
    ):
        self._did = did
        self.methods = methods or []
        self._id_base = id_base or "key"
        self._id_generator = self._default_id_generator()

    def _default_id_generator(self):
        """Default ID generator."""
        yield from _default_id_generator(self._id_base, start=len(self.methods))

    def add(
        self,
        type_: Type[VerificationMethod],
        ident: Optional[str] = None,
        controller: DID = None,
        **kwargs
    ):
        """Add verification method from parts and context."""
        ident = ident or next(self._id_generator)
        controller = controller or self._did
        vmethod = type_.make(id=self._did.ref(ident), controller=controller, **kwargs)
        self.methods.append(vmethod)
        return vmethod

    def remove(self, vmethod: VerificationMethod):
        """Remove method from builder."""
        self.methods.remove(vmethod)


class RelationshipBuilder(VerificationMethodBuilder):
    """Builder for relationships."""

    def __init__(
        self,
        did: DID,
        id_base: str,
        *,
        methods: Optional[List[Union[VerificationMethod, DIDUrl]]] = None
    ):
        super().__init__(did, id_base=id_base)
        self.methods = methods or []

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

    def reference(self, ref: DIDUrl):
        """Add reference to relationship."""
        if not isinstance(ref, DIDUrl):
            raise ValueError(
                "Reference must be DIDUrl, not {}".format(type(ref).__name__)
            )

        self.methods.append(ref)

    def embed(self, *args, **kwargs):
        """Embed verification method in relationship."""
        return super().add(*args, **kwargs)

    def remove(self, vmethod: Union[DIDUrl, VerificationMethod]):
        """Remove reference or method from builder."""
        self.methods.remove(vmethod)


class ServiceBuilder:
    """Builder for services."""

    def __init__(self, did: DID, *, services: Optional[List[Service]] = None):
        self._did = did
        self.services = services or []
        self._id_generator = _default_id_generator("service", start=len(self.services))

    def _determine_next_priority(self):
        """Return the next priority after the highest priority currently in services."""
        return (
            max(
                [
                    service.priority
                    for service in self.services
                    if isinstance(service, DIDCommService)
                ]
            )
            + 1
            if self.services
            else 0
        )

    def add(
        self, type_: str, service_endpoint: str, ident: Optional[str] = None, **extra
    ):
        """Add service."""
        ident = ident or next(self._id_generator)
        service = Service.make(
            id=self._did.ref(ident),
            type=type_,
            service_endpoint=service_endpoint,
            **extra
        )
        self.services.append(service)
        return service

    def add_didcomm(
        self,
        service_endpoint: str,
        recipient_keys: List[VerificationMethod],
        routing_keys: Optional[List[VerificationMethod]] = None,
        *,
        priority: Optional[int] = None,
        type_: Optional[str] = None,
        ident: Optional[str] = None,
        accept: Optional[List[str]] = None
    ):
        """Add DIDComm Service."""
        ident = ident or next(self._id_generator)
        routing_keys = routing_keys or []
        priority = priority or self._determine_next_priority()
        service = DIDCommService.make(
            id=self._did.ref(ident),
            service_endpoint=service_endpoint,
            recipient_keys=[vmethod.id for vmethod in recipient_keys],
            routing_keys=[vmethod.id for vmethod in routing_keys],
            type=type_,
            priority=priority,
            accept=accept,
        )
        self.services.append(service)
        return service

    def remove(self, service: Service):
        """Remove service from builder."""
        self.services.remove(service)


class DIDDocumentBuilder:
    """Builder for constructing DID Documents programmatically."""

    DEFAULT_CONTEXT = ["https://www.w3.org/ns/did/v1"]

    def __init__(
        self,
        id: Union[str, DID],
        context: List[str] = None,
        *,
        also_known_as: List[str] = None,
        controller: Union[List[str], List[DID]] = None
    ):
        """Initliaze builder."""
        self.id: DID = DID(id)
        self.context = context or self.DEFAULT_CONTEXT
        self.also_known_as = also_known_as
        self.controller = controller
        self.verification_method = VerificationMethodBuilder(self.id)
        self.authentication = RelationshipBuilder(self.id, "auth")
        self.assertion_method = RelationshipBuilder(self.id, "assert")
        self.key_agreement = RelationshipBuilder(self.id, "key-agreement")
        self.capability_invocation = RelationshipBuilder(
            self.id, "capability-invocation"
        )
        self.capability_delegation = RelationshipBuilder(
            self.id, "capability-delegation"
        )
        self.service = ServiceBuilder(self.id)
        self.extra = {}

    @classmethod
    def from_doc(cls, doc: DIDDocument) -> "DIDDocumentBuilder":
        """Create a Builder from an existing DIDDocument."""
        builder = cls(
            id=doc.id,
            context=doc.context,
            also_known_as=doc.also_known_as,
            controller=doc.controller,
        )
        builder.verification_method = VerificationMethodBuilder(
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
        builder.service = ServiceBuilder(doc.id, services=doc.service)
        return builder

    def build(self) -> DIDDocument:
        """Build document."""
        return DIDDocument.construct(
            id=self.id,
            context=self.context,
            also_known_as=self.also_known_as,
            controller=self.controller,
            verification_method=self.verification_method.methods or None,
            authentication=self.authentication.methods or None,
            assertion_method=self.assertion_method.methods or None,
            key_agreement=self.key_agreement.methods or None,
            capability_invocation=self.capability_invocation.methods or None,
            capability_delegation=self.capability_delegation.methods or None,
            service=self.service.services or None,
            **self.extra
        )
