# Generated migration for Phase 5.3
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("branding", "0001_initial"),
        ("user", "0010_migrate_professional_to_account"),
    ]

    operations = [
        migrations.AddField(
            model_name="brandtheme",
            name="account",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="brand_themes_new",
                to="user.account",
                help_text="Account that owns the theme.",
            ),
        ),
    ]
