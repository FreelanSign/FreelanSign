# backend/apps/legal_terms/tests/bdd/steps/test_legal_terms_assembly_steps.py
from typing import Any, Dict, List

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from apps.legal_terms.domain.entities.legal_profile import LegalProfile
from apps.legal_terms.domain.entities.legal_template import LegalTemplate
from apps.legal_terms.domain.exceptions import MandatoryClauseModificationError
from apps.legal_terms.domain.services.legal_terms_assembler import LegalTermsAssembler
from apps.legal_terms.domain.value_objects.clause_category import ClauseCategory
from apps.legal_terms.domain.value_objects.clause_content import ClauseContent

# Charge tous les scénarios du feature file
scenarios("../features/legal_terms_assembly.feature")


@pytest.fixture
def context() -> Dict[str, Any]:
    """
    Petit contexte partagé entre les steps pour stocker template, profil, résultat, exceptions, etc.
    """
    return {}


# ---------- GIVEN ----------


@given(
    parsers.parse(
        "un template légal avec les clauses suivantes\n{table}",
        extra_types={"table": str},
    )
)
def given_template_legal(context, table):
    """
    On construit un LegalTemplate de domaine à partir du tableau Gherkin.
    """
    # pytest-bdd fournit table sous forme de string, on utilise pytest-bdd's parse / simple split.
    # Pour simplifier, on va utiliser un parsing manuel des lignes.
    lines = [line.strip() for line in table.strip().splitlines() if line.strip()]
    # La première ligne commence par '|' => on split sur '|'
    headers = [h.strip() for h in lines[0].strip("|").split("|")]
    rows = [[c.strip() for c in line.strip("|").split("|")] for line in lines[1:]]

    clauses = []
    for row in rows:
        data = dict(zip(headers, row))
        identifier = data["identifier"]
        category = ClauseCategory.MANDATORY if data["category"] == "mandatory" else ClauseCategory.OPTIONAL
        default_title = data["default_title"]
        default_body = data["default_body"]
        default_order = int(data["default_order"])
        default_is_active = data["default_is_active"].lower() == "true"

        # Ici on suppose que LegalTemplate stocke les clauses sous forme de dicts ou de VO internes.
        # On reste agnostique: on prépare un dict "brut" que le LegalTemplate saura interpréter.
        clauses.append(
            {
                "identifier": identifier,
                "category": category,
                "default_content": {
                    "title": default_title,
                    "body": default_body,
                    "order": default_order,
                },
                "default_is_active": default_is_active,
            }
        )

    # Instanciation d'un LegalTemplate de domaine.
    # Adapte cette partie à ta vraie signature de LegalTemplate.
    template = LegalTemplate(
        jurisdiction="FR",
        version="1.0.0",
        name="CGV Auto-Entrepreneur FR",
        clauses=clauses,
    )

    context["template"] = template


@given("un profil légal sans overrides")
def given_empty_profile(context):
    template: LegalTemplate = context["template"]
    # On suppose que LegalProfile a une factory du style from_template(...) ou similaire.
    # Sinon, adapte avec ton vrai constructeur.
    profile = LegalProfile(
        template_version=template.version,
        clause_overrides={},  # profil vide = aucun override
    )
    context["profile"] = profile


@given(
    parsers.parse(
        "un profil légal avec les overrides suivants\n{table}",
        extra_types={"table": str},
    )
)
def given_profile_with_overrides(context, table):
    lines = [line.strip() for line in table.strip().splitlines() if line.strip()]
    headers = [h.strip() for h in lines[0].strip("|").split("|")]
    rows = [[c.strip() for c in line.strip("|").split("|")] for line in lines[1:]]

    overrides: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        data = dict(zip(headers, row))
        identifier = data["identifier"]
        is_active = data["is_active"].lower() == "true" if data["is_active"] else None
        custom_title = data["custom_title"] or None
        custom_body = data["custom_body"] or None
        custom_order = int(data["custom_order"]) if data["custom_order"] else None

        override: Dict[str, Any] = {}
        if is_active is not None:
            override["is_active"] = is_active
        if custom_title is not None:
            override["custom_title"] = custom_title
        if custom_body is not None:
            override["custom_body"] = custom_body
        if custom_order is not None:
            override["custom_order"] = custom_order

        overrides[identifier] = override

    template: LegalTemplate = context["template"]
    profile = LegalProfile(
        template_version=template.version,
        clause_overrides=overrides,
    )
    context["profile"] = profile


# ---------- WHEN ----------


@when("j'assemble les termes légaux")
def when_assemble_terms(context):
    template: LegalTemplate = context["template"]
    profile: LegalProfile = context["profile"]

    assembler = LegalTermsAssembler()
    # On considère que assemble renvoie une liste de ClauseContent / RenderedClause.
    rendered_clauses: List[ClauseContent] = assembler.assemble(template, profile)
    context["rendered_clauses"] = rendered_clauses
    context["error"] = None


@when("j'essaie d'assembler les termes légaux")
def when_try_assemble_terms(context):
    template: LegalTemplate = context["template"]
    profile: LegalProfile = context["profile"]

    assembler = LegalTermsAssembler()
    try:
        rendered_clauses = assembler.assemble(template, profile)
        context["rendered_clauses"] = rendered_clauses
        context["error"] = None
    except Exception as exc:
        context["rendered_clauses"] = None
        context["error"] = exc


# ---------- THEN ----------


@then(parsers.parse("j'obtiens {count:d} clauses rendues"))
def then_clause_count(context, count: int):
    rendered_clauses: List[ClauseContent] = context["rendered_clauses"]
    assert len(rendered_clauses) == count


@then(parsers.parse('la clause "{identifier}" est présente et obligatoire'))
def then_clause_present_and_mandatory(context, identifier: str):
    rendered_clauses: List[ClauseContent] = context["rendered_clauses"]
    clause = next((c for c in rendered_clauses if c.identifier == identifier), None)
    assert clause is not None
    assert clause.is_mandatory is True


@then(parsers.parse('la clause "{identifier}" est présente et optionnelle'))
def then_clause_present_and_optional(context, identifier: str):
    rendered_clauses: List[ClauseContent] = context["rendered_clauses"]
    clause = next((c for c in rendered_clauses if c.identifier == identifier), None)
    assert clause is not None
    assert clause.is_mandatory is False


@then(parsers.parse('la clause "{identifier}" n\'est pas présente dans le résultat'))
def then_clause_not_present(context, identifier: str):
    rendered_clauses: List[ClauseContent] = context["rendered_clauses"]
    assert all(c.identifier != identifier for c in rendered_clauses)


@then("une erreur de modification de clause obligatoire est levée")
def then_mandatory_clause_error(context):
    error = context["error"]
    assert isinstance(error, MandatoryClauseModificationError)
