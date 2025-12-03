"""
LegalTermsAssembler domain service.
Combines template + profile overrides to produce final clause list.
"""
from typing import Any

from apps.legal_terms.domain.entities.legal_profile import LegalProfile
from apps.legal_terms.domain.entities.legal_template import LegalTemplate
from apps.legal_terms.domain.value_objects.clause_category import ClauseCategory
from apps.legal_terms.domain.value_objects.clause_content import ClauseContent


class LegalTermsAssembler:
    """
    Domain service that assembles final legal terms.
    Combines template clauses with profile overrides and enforces business rules.
    """

    def assemble(
        self,
        template: LegalTemplate,
        profile: LegalProfile,
    ) -> list[ClauseContent]:
        """
        Assemble final clause list by merging template and profile.

        Business rules:
        - Mandatory clauses always included and active
        - Optional clauses can be toggled via profile
        - Profile overrides apply to title, body, order
        - Clauses are returned in order
        """
        assembled_clauses: list[ClauseContent] = []

        for clause_data in template.get_default_clauses():
            identifier = clause_data["identifier"]
            is_mandatory = clause_data.get("category") == ClauseCategory.MANDATORY
            default_is_active = clause_data.get("default_is_active", True)

            # Get override from profile
            override = profile.get_override(identifier)

            # Determine if clause is active
            if is_mandatory:
                # Mandatory clauses always active
                is_active = True
            else:
                # Optional clauses: use override or default
                if override and "is_active" in override:
                    is_active = override["is_active"]
                else:
                    is_active = default_is_active

            # Skip inactive clauses
            if not is_active:
                continue

            # Determine final content
            title = clause_data.get("default_title", "")
            body = clause_data.get("default_body", "")
            order = clause_data.get("default_order", 0)
            was_customized = False

            if override:
                if "custom_title" in override:
                    title = override["custom_title"]
                    was_customized = True
                if "custom_body" in override:
                    body = override["custom_body"]
                    was_customized = True
                if "custom_order" in override:
                    order = override["custom_order"]

            clause_content = ClauseContent(
                identifier=identifier,
                title=title,
                body=body,
                order=order,
                is_mandatory=is_mandatory,
                was_customized=was_customized,
            )
            assembled_clauses.append(clause_content)

        # Sort by order
        assembled_clauses.sort(key=lambda c: c.order)

        return assembled_clauses

    def create_snapshot_data(
        self,
        clauses: list[ClauseContent],
        template: LegalTemplate,
        variables_dict: dict[str, str],
    ) -> dict[str, Any]:
        """
        Create snapshot data for AttachedTerms.
        """
        return {
            "template_version": template.version,
            "template_name": template.name,
            "clauses": [
                {
                    "identifier": clause.identifier,
                    "title": clause.title,
                    "body": clause.body,
                    "order": clause.order,
                    "is_mandatory": clause.is_mandatory,
                    "was_customized": clause.was_customized,
                }
                for clause in clauses
            ],
            "variables_used": variables_dict,
        }
