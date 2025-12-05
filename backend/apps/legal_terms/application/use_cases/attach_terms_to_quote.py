"""
Use case for attaching legal terms to a quote.
"""

import uuid

from apps.legal_terms.application.dtos.attach_dto import (
    AttachTermsInput,
    AttachTermsOutput,
)
from apps.legal_terms.application.ports.account_service import AccountService
from apps.legal_terms.application.ports.attached_terms_repository import (
    AttachedTermsRepository,
)
from apps.legal_terms.application.ports.legal_profile_repository import (
    LegalProfileRepository,
)
from apps.legal_terms.application.ports.legal_template_repository import (
    LegalTemplateRepository,
)
from apps.legal_terms.application.ports.template_renderer import TemplateRenderer
from apps.legal_terms.domain.entities.attached_terms import AttachedTerms
from apps.legal_terms.domain.exceptions import NoActiveTemplateError
from apps.legal_terms.domain.services.legal_terms_assembler import LegalTermsAssembler


class AttachTermsToQuoteUseCase:
    """Use case for attaching legal terms to a quote."""

    def __init__(
        self,
        profile_repository: LegalProfileRepository,
        template_repository: LegalTemplateRepository,
        attached_terms_repository: AttachedTermsRepository,
        account_service: AccountService,
        template_renderer: TemplateRenderer,
        assembler: LegalTermsAssembler,
        default_jurisdiction: str = "FR",
    ):
        self.profile_repository = profile_repository
        self.template_repository = template_repository
        self.attached_terms_repository = attached_terms_repository
        self.account_service = account_service
        self.template_renderer = template_renderer
        self.assembler = assembler
        self.default_jurisdiction = default_jurisdiction

    def execute(self, input_dto: AttachTermsInput) -> AttachTermsOutput:
        """
        Attach legal terms to a quote.
        Loads template, profile, assembles clauses, renders, and persists snapshot.
        Raises exceptions if prerequisites are missing.
        """
        # Get active template
        template = self.template_repository.get_active_for_jurisdiction(self.default_jurisdiction)
        if not template:
            raise NoActiveTemplateError(self.default_jurisdiction)

        # Get or create profile
        profile = self.profile_repository.get_or_create_for_account(
            account_id=input_dto.account_id,
            template_id=template.id,
            template_version=template.version,
        )

        # Get template variables (raises MissingTemplateVariablesError if missing)
        variables = self.account_service.get_template_variables(input_dto.account_id)

        # Assemble clauses
        clauses = self.assembler.assemble(template, profile)

        # Render
        rendered_html, rendered_text = self.template_renderer.render(clauses, variables)

        # Create snapshot data
        snapshot_data = self.assembler.create_snapshot_data(clauses, template, variables.to_dict())

        # Create AttachedTerms entity
        attached_terms = AttachedTerms(
            id=str(uuid.uuid4()),
            quote_id=input_dto.quote_id,
            template_version=template.version,
            rendered_html=rendered_html,
            rendered_text=rendered_text,
            snapshot_data=snapshot_data,
        )

        # Persist
        saved_terms = self.attached_terms_repository.save(attached_terms)

        return AttachTermsOutput(
            attached_terms_id=saved_terms.id,
            template_version=saved_terms.template_version,
        )
