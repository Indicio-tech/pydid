"""DID Document Object."""

from contextlib import contextmanager
from typing import Any, ContextManager, Iterable, List, Set, Union

from voluptuous import ALLOW_EXTRA, All, Coerce, Switch, Url

from ..did import DID
from ..did_url import DIDUrl
from ..validation import (
    Option,
    Properties,
    serialize,
    single_to_list,
    unwrap_if_list_of_one,
    validate_init,
    wrap_validation_error,
)
from . import DIDDocumentError
from .didcomm_service import DIDCommService
from .doc_options import DIDDocumentOption
from .service import Service
from .verification_method import VerificationMethod, VerificationSuite
from .verification_relationship import VerificationRelationship


class IdentifiedResourceMismatch(DIDDocumentError):
    """Raised when two or more of the same ID point to differing resources."""


class ResourceIDNotFound(DIDDocumentError):
    """Raised when Resource ID not found in DID Document."""


class DIDDocumentValidationError(DIDDocumentError):
    """Raised when Document validation fails."""


class DIDDocument:
    """Representation of DID Document."""

    properties = Properties(extra=ALLOW_EXTRA)

    def __init__(
        self,
        id: Union[str, DID],
        context: List[Any],
        *,
        also_known_as: List[str] = None,
        controller: List[str] = None,
        verification_method: List[VerificationMethod] = None,
        authentication: VerificationRelationship = None,
        assertion_method: VerificationRelationship = None,
        key_agreement: VerificationRelationship = None,
        capability_invocation: VerificationRelationship = None,
        capability_delegation: VerificationRelationship = None,
        service: List[Service] = None,
        **extra
    ):
        """Create DIDDocument."""
        self._id = id
        self._context = context
        self._also_known_as = also_known_as
        self._controller = controller
        self._verification_method = verification_method
        self._authentication = authentication
        self._assertion_method = assertion_method
        self._key_agreement = key_agreement
        self._capability_invocation = capability_invocation
        self._capability_delegation = capability_delegation
        self._service = service
        self.extra = extra

        self._index = {}
        self._index_resources()

    def _index_resources(self):
        """Index resources by ID.

        IDs are not guaranteed to be unique within the document.
        The first instance is stored in the index and subsequent id collisions
        are checked against the original. If they do not match, an error will
        be thrown.
        """

        def _indexer(item):
            if not item:
                # Attribute isn't set
                return
            if isinstance(item, DIDUrl):
                # We don't index references
                return
            if isinstance(item, list):
                for subitem in item:
                    _indexer(subitem)
                return
            if isinstance(item, VerificationRelationship):
                for subitem in item.items:
                    _indexer(subitem)
                return

            assert isinstance(item, (VerificationMethod, Service))
            if item.id in self._index and item != self._index[item.id]:
                raise IdentifiedResourceMismatch(
                    "ID {} already found in Index and Items do not match".format(
                        item.id
                    )
                )

            self._index[item.id] = item

        for item in (
            self.verification_method,
            self.authentication,
            self.assertion_method,
            self.key_agreement,
            self.capability_invocation,
            self.capability_delegation,
            self.service,
        ):
            _indexer(item)

    @property
    @properties.add(
        data_key="@context",
        required=True,
        validate=Switch(Url(), [Url()], dict, [dict]),
        serialize=unwrap_if_list_of_one,
        deserialize=single_to_list,
    )
    def context(self):
        """Return context."""
        return self._context

    @property
    @properties.add(
        required=True,
        validate=All(str, DID.validate),
        serialize=Coerce(str),
        deserialize=Coerce(DID),
    )
    def id(self):
        """Return id."""
        return self._id

    @property
    @properties.add(data_key="alsoKnownAs", validate=[str])
    def also_known_as(self):
        """Return also_known_as."""
        return self._also_known_as

    @property
    @properties.add(
        validate=Switch(All(str, DID.validate), [DID.validate]),
        serialize=All([Coerce(str)], unwrap_if_list_of_one),
        deserialize=All(single_to_list, [Coerce(DID)]),
    )
    def controller(self):
        """Return controller."""
        return self._controller

    @property
    @properties.add(
        data_key="verificationMethod",
        validate=[VerificationMethod.validate],
        serialize=[serialize],
        deserialize=[VerificationMethod.deserialize],
    )
    def verification_method(self):
        """Return verification_method."""
        return self._verification_method

    @property
    @properties.add(
        validate=VerificationRelationship.validate,
        serialize=serialize,
        deserialize=VerificationRelationship.deserialize,
    )
    def authentication(self):
        """Return authentication."""
        return self._authentication

    @property
    @properties.add(
        data_key="assertionMethod",
        validate=VerificationRelationship.validate,
        serialize=serialize,
        deserialize=VerificationRelationship.deserialize,
    )
    def assertion_method(self):
        """Return assertion_method."""
        return self._assertion_method

    @property
    @properties.add(
        data_key="keyAgreement",
        validate=VerificationRelationship.validate,
        serialize=serialize,
        deserialize=VerificationRelationship.deserialize,
    )
    def key_agreement(self):
        """Return key_agreement."""
        return self._key_agreement

    @property
    @properties.add(
        data_key="capabilityInvocation",
        validate=VerificationRelationship.validate,
        serialize=serialize,
        deserialize=VerificationRelationship.deserialize,
    )
    def capability_invocation(self):
        """Return capability_invocation."""
        return self._capability_invocation

    @property
    @properties.add(
        data_key="capabilityDelegation",
        validate=VerificationRelationship.validate,
        serialize=serialize,
        deserialize=VerificationRelationship.deserialize,
    )
    def capability_delegation(self):
        """Return capability_delegation."""
        return self._capability_delegation

    @property
    @properties.add(
        validate=[Service.validate],
        serialize=[serialize],
        deserialize=[Service.deserialize],
    )
    def service(self):
        """Return service."""
        return self._service

    def dereference(self, reference: Union[str, DIDUrl]):
        """Dereference a DID URL to a document resource."""
        if isinstance(reference, str):
            reference = DIDUrl.parse(reference)

        if reference not in self._index:
            raise ResourceIDNotFound("ID {} not found in document".format(reference))
        return self._index[reference]

    @classmethod
    @wrap_validation_error(
        DIDDocumentValidationError, message="Failed to validate DID Document"
    )
    def validate(cls, value):
        """Validate against expected schema."""
        return cls.properties.validate(value)

    @wrap_validation_error(DIDDocumentError, message="Failed to serialize DID Document")
    def serialize(self):
        """Serialize DID Document."""
        value = self.properties.serialize(self)
        return {**value, **self.extra}

    @classmethod
    @wrap_validation_error(
        DIDDocumentValidationError, message="Failed to deserialize DID Document"
    )
    def deserialize(cls, value: dict, options: Set[Option] = None):
        """Deserialize DID Document."""
        if options:
            value = DIDDocumentOption.apply(value, options)
        value = cls.validate(value)
        value = cls.properties.deserialize(value)
        return cls(**value)

    def to_builder(self):
        """Return a builder from this doc."""
        return DIDDocumentBuilder.from_doc(self)


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
