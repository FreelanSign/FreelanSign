# apps/quote/tests/conftest.py
import pytest
from django.apps import apps as django_apps


@pytest.fixture
def client_model():
    """
    Return the Client model class used by the project.

    This fixture attempts to resolve the model dynamically so tests
    don't hardcode the app label. It tries several common app labels.
    """
    # Try common app labels where the Client model might live.
    candidates = [
        ("client", "Client"),
        ("clients", "Client"),
        ("app_client", "Client"),
        ("apps.client", "Client"),
        ("apps.client", "Client"),  # harmless duplicate
    ]
    last_exc = None
    for app_label, model_name in candidates:
        try:
            model = django_apps.get_model(app_label, model_name)
            if model is not None:
                return model
        except LookupError as e:
            last_exc = e
            continue

    # If not found, raise a helpful error so you can add the correct app_label.
    raise LookupError(
        "Could not find Client model. Please adjust the 'candidates' list in "
        "apps/quote/tests/conftest.py or import your Client model directly into the test."
    )
