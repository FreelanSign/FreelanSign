# Generated migration for Phase 5.4
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_remove_prestation_unique_area_prestation_name_and_more"),
        ("user", "0010_migrate_professional_to_account"),
    ]

    operations = [
        migrations.AddField(
            model_name="prestation",
            name="account",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="custom_prestations_new",
                to="user.account",
                help_text="Account that created this custom prestation.",
            ),
        ),
    ]
