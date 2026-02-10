# Generated migration for Phase 5.4 - Finalize account FK
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0004_migrate_to_account"),
        ("user", "0010_migrate_professional_to_account"),
    ]

    operations = [
        # Update account field - change related_name from custom_prestations_new to custom_prestations
        migrations.AlterField(
            model_name="prestation",
            name="account",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="custom_prestations",
                to="user.account",
                help_text="Account that created this custom prestation.",
            ),
        ),
        # Remove old constraint
        migrations.RemoveConstraint(
            model_name="prestation",
            name="unique_professional_prestation_name",
        ),
        # Add new constraint for account
        migrations.AddConstraint(
            model_name="prestation",
            constraint=models.UniqueConstraint(
                fields=["account", "name"],
                condition=models.Q(account__isnull=False),
                name="unique_account_prestation_name",
            ),
        ),
        # Remove old index
        migrations.RemoveIndex(
            model_name="prestation",
            name="idx_prest_professional_user",
        ),
        # Add new index for account
        migrations.AddIndex(
            model_name="prestation",
            index=models.Index(fields=["account"], name="idx_prest_account"),
        ),
        # Drop professional_user field
        migrations.RemoveField(
            model_name="prestation",
            name="professional_user",
        ),
    ]
