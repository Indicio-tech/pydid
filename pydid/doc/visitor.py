"""Visitor class for manipulating DID documents."""

from abc import ABC


class DocVisitor(ABC):
    """Visitor class for manipulating the document."""

    def __init__(self, document: dict):
        self.document = document

    def visit_verification_method(self, value: dict):
        """Visit a verification method."""
        return value

    def visit_service(self, value: dict):
        """Visit a service."""
        return value

    def visit_value_with_id(self, value: dict):
        """Visit a value with an id."""
        return value

    def visit_verification_relationship_ref(self, value: str):
        """Visit a verification relationship."""
        return value

    def visit_verification_relationship_embedded(self, value: dict):
        """Visit an embedded verification method."""
        return value

    def visit_authentication_ref(self, value: str):
        """Visit an authentication relationship."""
        return value

    def visit_authentication_embedded(self, value: dict):
        """Visit an embedded authentication relationship."""
        return value

    def visit_key_agreement_ref(self, value: str):
        """Visit a key agreement relationship."""
        return value

    def visit_key_agreement_embedded(self, value: dict):
        """Visit an embedded key agreement relationship."""
        return value

    def visit_assertion_method_ref(self, value: str):
        """Visit an assertion method relationship."""
        return value

    def visit_assertion_method_embedded(self, value: dict):
        """Visit an embedded assertion method relationship."""
        return value

    def visit_capability_delegation_ref(self, value: str):
        """Visit a capability delegation relationship."""
        return value

    def visit_capability_delegation_embedded(self, value: dict):
        """Visit an embedded capability delegation relationship."""
        return value

    def visit_capability_invocation_ref(self, value: str):
        """Visit a capability invocation relationship."""
        return value

    def visit_capability_invocation_embedded(self, value: dict):
        """Visit an embedded capability invocation relationship."""
        return value

    def visit(self):
        """Visit the document."""
        vms = []
        for value in self.document["verificationMethod"]:
            value = self.visit_value_with_id(value)
            value = self.visit_verification_method(value)
            vms.append(value)
        self.document["verificationMethod"] = vms

        services = []
        for value in self.document["service"]:
            value = self.visit_value_with_id(value)
            value = self.visit_service(value)
            services.append(value)
        self.document["service"] = services

        authentication = []
        for value in self.document["authentication"]:
            if isinstance(value, str):
                value = self.visit_verification_relationship_ref(value)
                value = self.visit_authentication_ref(value)
            if isinstance(value, dict):
                value = self.visit_value_with_id(value)
                value = self.visit_verification_relationship_embedded(value)
                value = self.visit_authentication_embedded(value)
            authentication.append(value)
        self.document["authentication"] = authentication

        key_agreement = []
        for value in self.document["keyAgreement"]:
            if isinstance(value, str):
                value = self.visit_verification_relationship_ref(value)
                value = self.visit_key_agreement_ref(value)
            if isinstance(value, dict):
                value = self.visit_value_with_id(value)
                value = self.visit_verification_relationship_embedded(value)
                value = self.visit_key_agreement_embedded(value)
            key_agreement.append(value)
        self.document["keyAgreement"] = key_agreement

        assertion_method = []
        for value in self.document["assertionMethod"]:
            if isinstance(value, str):
                value = self.visit_verification_relationship_ref(value)
                value = self.visit_assertion_method_ref(value)
            if isinstance(value, dict):
                value = self.visit_value_with_id(value)
                value = self.visit_verification_relationship_embedded(value)
                value = self.visit_assertion_method_embedded(value)
            assertion_method.append(value)
        self.document["assertionMethod"] = assertion_method

        capability_delegation = []
        for value in self.document["capabilityDelegation"]:
            if isinstance(value, str):
                value = self.visit_verification_relationship_ref(value)
                value = self.visit_capability_delegation_ref(value)
            if isinstance(value, dict):
                value = self.visit_value_with_id(value)
                value = self.visit_verification_relationship_embedded(value)
                value = self.visit_capability_delegation_embedded(value)
            capability_delegation.append(value)
        self.document["capabilityDelegation"] = capability_delegation

        capability_invocation = []
        for value in self.document["capabilityInvocation"]:
            if isinstance(value, str):
                value = self.visit_verification_relationship_ref(value)
                value = self.visit_capability_invocation_ref(value)
            if isinstance(value, dict):
                value = self.visit_value_with_id(value)
                value = self.visit_verification_relationship_embedded(value)
                value = self.visit_capability_invocation_embedded(value)
            capability_invocation.append(value)
        self.document["capabilityInvocation"] = capability_invocation

        return self.document
