"""
Use case for previewing legal terms.
"""

from apps.legal_terms.application.dtos.preview_dto import (
    ClausePreviewDTO,
    PreviewLegalTermsInput,
    PreviewLegalTermsOutput,
)
from apps.legal_terms.application.ports.account_service import AccountService
from apps.legal_terms.application.ports.legal_profile_repository import (
    LegalProfileRepository,
)
from apps.legal_terms.application.ports.legal_template_repository import (
    LegalTemplateRepository,
)
from apps.legal_terms.application.ports.template_renderer import TemplateRenderer
from apps.legal_terms.domain.exceptions import NoActiveTemplateError
from apps.legal_terms.domain.services.legal_terms_assembler import LegalTermsAssembler


class PreviewLegalTermsUseCase:
    """Use case for previewing legal terms for an account."""

    def __init__(
        self,
        profile_repository: LegalProfileRepository,
        template_repository: LegalTemplateRepository,
        account_service: AccountService,
        template_renderer: TemplateRenderer,
        assembler: LegalTermsAssembler,
        default_jurisdiction: str = "FR",
    ):
        self.profile_repository = profile_repository
        self.template_repository = template_repository
        self.account_service = account_service
        self.template_renderer = template_renderer
        self.assembler = assembler
        self.default_jurisdiction = default_jurisdiction

    def execute(self, input_dto: PreviewLegalTermsInput) -> PreviewLegalTermsOutput:
        """
        Preview legal terms for an account.
        Loads or creates profile, assembles clauses, and renders preview.
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

        # Get template variables
        variables = self.account_service.get_template_variables(input_dto.account_id)

        # Assemble clauses
        clauses = self.assembler.assemble(template, profile)

        # Render
        rendered_html, rendered_text = self.template_renderer.render(clauses, variables)

        # Convert to DTOs
        clause_dtos = [
            ClausePreviewDTO(
                identifier=clause.identifier,
                title=clause.title,
                body=clause.body,
                order=clause.order,
                is_mandatory=clause.is_mandatory,
                was_customized=clause.was_customized,
            )
            for clause in clauses
        ]

        return PreviewLegalTermsOutput(
            clauses=clause_dtos,
            rendered_html=rendered_html,
            rendered_text=rendered_text,
            template_version=template.version,
        )
