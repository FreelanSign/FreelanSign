# apps/user/tests/test_professional_serializer_minimal.py
import pytest
from django.contrib.auth import get_user_model

from apps.catalog.models import Area, Prestation
from apps.user.application.dto.user_viewmodels import ProfessionalViewModel
from apps.user.interface.serializers import ProfessionalOutputSerializer

User = get_user_model()


@pytest.mark.django_db
def test_professional_output_contains_service_type_ids():
    area = Area.objects.create(name="A")
    p1 = Prestation.objects.create(area=area, name="P1", default_rate_cents=1000)
    p2 = Prestation.objects.create(area=area, name="P2", default_rate_cents=2000)

    user = User.objects.create_user(email="pro@example.test", password="pwd")
    # on simule une VM (le serializer est VM-based)
    vm = ProfessionalViewModel(
        id=1,
        user_id=user.id,
        name="Pro",
        status_juridique=None,
        domaine_id=area.id,
        domaine_name=area.name,
        tjm_cents=45000,
        tjm_display="450.00",
        number_pro=None,
        service_type_ids=[p1.id, p2.id],
        created_at=user.date_joined,
        updated_at=user.date_joined,
    )
    data = ProfessionalOutputSerializer.from_vm(vm).data
    assert sorted(data["service_type_ids"]) == sorted([p1.id, p2.id])
