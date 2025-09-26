from apps.user.interface.serializers import ProfessionalUserSerializer
import pytest
from django.contrib.auth import get_user_model
from apps.catalog.models import Area, Prestation
from apps.user.models.models import ProfessionalUser

User = get_user_model()

@pytest.mark.django_db
def test_service_types_off_domain_flag(client):
    # setup areas
    area_a = Area.objects.create(name="A")
    area_b = Area.objects.create(name="B")
    area_c = Area.objects.create(name="C")

    # prestations
    p_a = Prestation.objects.create(area=area_a, name="prest A", default_rate_cents=1000)
    p_b = Prestation.objects.create(area=area_b, name="prest B", default_rate_cents=2000)
    p_c = Prestation.objects.create(area=area_c, name="prest C", default_rate_cents=3000)

    # user + professional
    user = User.objects.create_user(email="pro@example.test", password="pwd")
    prof = ProfessionalUser.objects.create(user=user, name="Pro", domaine=area_a)
    # allowed_areas includes area_b, so p_b ok; p_c should be off_domain
    prof.service_types.set([p_a, p_b, p_c])
    prof.allowed_areas.set([area_b])

    serializer = ProfessionalUserSerializer(prof, context={"request": None})
    data = serializer.data
    meta = {m['id']: m for m in data['service_types_meta']}
    assert meta[p_a.id]['off_domain'] is False
    assert meta[p_b.id]['off_domain'] is False
    assert meta[p_c.id]['off_domain'] is True
