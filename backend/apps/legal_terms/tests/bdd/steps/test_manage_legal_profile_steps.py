"""
BDD step definitions for managing legal profile.
"""

import pytest
from django.urls import reverse
from pytest_bdd import given, parsers, scenario, then, when
from rest_framework import status

from apps.legal_terms.adapters.persistence.models import (
    LegalProfileModel,
    LegalTemplateModel,
)


# Scenarios
@pytest.mark.skip(reason="Address field not yet in Account model - MVP limitation")
@scenario("../features/manage_legal_profile.feature", "L'utilisateur active une clause optionnelle et la voit dans l'aperçu")
def test_user_activates_optional_clause():
    """User activates an optional clause and sees it in preview."""
    pass


@pytest.mark.skip(reason="Address field not yet in Account model - MVP limitation")
@scenario(
    "../features/manage_legal_profile.feature", "L'utilisateur personnalise le texte d'une clause et le voit dans l'aperçu"
)
def test_user_customizes_clause_text():
    """User customizes clause text and sees it in preview."""
    pass


@pytest.mark.skip(reason="Address field not yet in Account model - MVP limitation")
@scenario("../features/manage_legal_profile.feature", "L'utilisateur ne peut pas désactiver une clause obligatoire")
def test_user_cannot_disable_mandatory_clause():
    """User cannot disable a mandatory clause."""
    pass


@pytest.mark.skip(reason="Address field not yet in Account model - MVP limitation")
@scenario("../features/manage_legal_profile.feature", "L'utilisateur désactive une clause optionnelle")
def test_user_disables_optional_clause():
    """User disables an optional clause."""
    pass


@pytest.mark.skip(reason="Address field not yet in Account model - MVP limitation")
@scenario("../features/manage_legal_profile.feature", "Les variables sont substituées dans l'aperçu")
def test_variables_are_substituted_in_preview():
    """Variables are substituted in preview."""
    pass


# Given steps
@given(parsers.parse('un template légal actif "{template_name}" avec les clauses:'), target_fixture="legal_template")
def legal_template_with_clauses(template_name, db, datatable):
    """Create a legal template with clauses from datatable."""
    clauses = []
    headers = datatable[0]
    for row_data in datatable[1:]:
        row_dict = dict(zip(headers, row_data))
        clauses.append(
            {
                "identifier": row_dict["identifiant"],
                "category": row_dict["catégorie"],
                "default_title": row_dict["titre"],
                "default_body": row_dict["contenu"],
                "default_order": int(row_dict["ordre"]),
                "default_is_active": row_dict["actif"].lower() == "true",
            }
        )

    # Try to get existing template first, or create new one
    try:
        template = LegalTemplateModel.objects.get(jurisdiction="FR", version="1.0.0")
        # Update clauses for the test
        template.clauses = clauses
        template.save()
        return template
    except LegalTemplateModel.DoesNotExist:
        return LegalTemplateModel.objects.create(
            name=template_name,
            jurisdiction="FR",
            version="1.0.0",
            is_active=True,
            clauses=clauses,
        )


@given("un compte avec les données légales requises", target_fixture="account_with_legal_data")
def account_with_legal_data(user_with_account):
    """Create account with required legal data."""
    user, account = user_with_account

    # Set required legal fields
    account.legal_id = "12345678901234"
    account.display_name = "ACME Corp"
    account.save()

    # Set phone on profile
    profile = user.profile
    profile.phone = "+33 1 23 45 67 89"
    profile.save()

    return user, account


@given("un compte avec les données légales:", target_fixture="account_with_custom_legal_data")
def account_with_custom_legal_data(user_with_account, datatable):
    """Create account with custom legal data from datatable."""
    user, account = user_with_account

    data_map = {row["champ"]: row["valeur"] for row in datatable}

    account.legal_id = data_map.get("SIRET")
    account.display_name = data_map.get("nom")
    account.save()

    profile = user.profile
    profile.phone = data_map.get("téléphone")
    profile.save()

    # Note: email comes from User model
    user.email = data_map.get("email", user.email)
    user.save()

    return user, account


@given("je suis connecté")
def user_logged_in(api_client, account_with_legal_data):
    """Log in the user."""
    user, account = account_with_legal_data
    api_client.force_login(user)


@given(parsers.parse('le template contient une clause avec "{content}"'))
def template_with_clause_content(legal_template, content):
    """Add a clause with specific content to the template."""
    # Update first clause to have this content
    clauses = legal_template.clauses
    if clauses:
        clauses[0]["default_body"] = content
        legal_template.clauses = clauses
        legal_template.save()


# When steps
@when(parsers.parse('j\'active la clause "{identifier}"'), target_fixture="patch_response")
def activate_clause(api_client, identifier):
    """Activate a clause via PATCH."""
    url = reverse("legal_terms:legal-profile")
    payload = {
        "updates": [
            {
                "identifier": identifier,
                "is_active": True,
            }
        ]
    }
    response = api_client.patch(url, payload, format="json")
    return response


@when(parsers.parse('je désactive la clause "{identifier}"'), target_fixture="patch_response")
def deactivate_clause(api_client, identifier):
    """Deactivate a clause via PATCH."""
    url = reverse("legal_terms:legal-profile")
    payload = {
        "updates": [
            {
                "identifier": identifier,
                "is_active": False,
            }
        ]
    }
    response = api_client.patch(url, payload, format="json")
    return response


@when(parsers.parse('je modifie le titre de la clause "{identifier}" en "{title}"'))
def modify_clause_title(api_client, identifier, title):
    """Modify clause title via PATCH."""
    url = reverse("legal_terms:legal-profile")
    payload = {
        "updates": [
            {
                "identifier": identifier,
                "custom_title": title,
            }
        ]
    }
    response = api_client.patch(url, payload, format="json")
    assert response.status_code == status.HTTP_200_OK


@when(parsers.parse('je modifie le contenu de la clause "{identifier}" en "{body}"'))
def modify_clause_body(api_client, identifier, body):
    """Modify clause body via PATCH."""
    url = reverse("legal_terms:legal-profile")
    payload = {
        "updates": [
            {
                "identifier": identifier,
                "custom_body": body,
            }
        ]
    }
    response = api_client.patch(url, payload, format="json")
    assert response.status_code == status.HTTP_200_OK


@when(parsers.parse('j\'essaie de désactiver la clause "{identifier}"'), target_fixture="patch_error_response")
def try_deactivate_mandatory_clause(api_client, identifier):
    """Try to deactivate a mandatory clause."""
    url = reverse("legal_terms:legal-profile")
    payload = {
        "updates": [
            {
                "identifier": identifier,
                "is_active": False,
            }
        ]
    }
    response = api_client.patch(url, payload, format="json")
    return response


@when("je consulte l'aperçu des conditions légales", target_fixture="preview_response")
def get_preview(api_client):
    """Get preview of legal terms."""
    url = reverse("legal_terms:legal-preview")
    response = api_client.get(url)
    return response


# Then steps
@then(parsers.parse('l\'aperçu contient la clause "{identifier}"'))
def preview_contains_clause(preview_response, identifier):
    """Check that preview contains a specific clause."""
    assert preview_response.status_code == status.HTTP_200_OK
    data = preview_response.json()

    clause = next((c for c in data["clauses"] if c["identifier"] == identifier), None)
    assert clause is not None, f"Clause '{identifier}' not found in preview"


@then(parsers.parse('l\'aperçu ne contient pas la clause "{identifier}"'))
def preview_does_not_contain_clause(preview_response, identifier):
    """Check that preview does not contain a specific clause."""
    assert preview_response.status_code == status.HTTP_200_OK
    data = preview_response.json()

    clause = next((c for c in data["clauses"] if c["identifier"] == identifier), None)
    assert clause is None, f"Clause '{identifier}' should not be in preview"


@then(parsers.parse('la clause "{identifier}" est marquée comme personnalisée'))
def clause_is_marked_as_customized(preview_response, identifier):
    """Check that clause is marked as customized."""
    data = preview_response.json()

    clause = next((c for c in data["clauses"] if c["identifier"] == identifier), None)
    assert clause is not None
    assert clause["was_customized"] is True


@then(parsers.parse('l\'aperçu contient le titre "{title}"'))
def preview_contains_title(preview_response, title):
    """Check that preview HTML contains a specific title."""
    data = preview_response.json()
    assert title in data["rendered_html"]


@then(parsers.parse('l\'aperçu contient le texte "{text}"'))
def preview_contains_text(preview_response, text):
    """Check that preview contains specific text."""
    data = preview_response.json()
    assert text in data["rendered_html"]


@then(parsers.parse('l\'aperçu contient "{text}"'))
def preview_contains_generic_text(preview_response, text):
    """Check that preview contains text (generic)."""
    data = preview_response.json()
    assert text in data["rendered_html"]


@then(parsers.parse('l\'aperçu ne contient pas "{text}"'))
def preview_does_not_contain_text(preview_response, text):
    """Check that preview does not contain text."""
    data = preview_response.json()
    assert text not in data["rendered_html"]


@then("je reçois une erreur indiquant que les clauses obligatoires ne peuvent pas être désactivées")
def receive_mandatory_clause_error(patch_error_response):
    """Check that error is returned for mandatory clause modification."""
    assert patch_error_response.status_code == status.HTTP_400_BAD_REQUEST
    data = patch_error_response.json()
    assert "error" in data
    assert "mandatory" in data["error"].lower() or "obligatoire" in data["error"].lower()
