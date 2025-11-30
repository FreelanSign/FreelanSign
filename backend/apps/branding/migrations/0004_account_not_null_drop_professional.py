# Generated migration for Phase 5.3 - Finalize account FK
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("branding", "0003_migrate_to_account"),
        ("user", "0010_migrate_professional_to_account"),
    ]

    operations = [
        # Make account NOT NULL and update related_name
        migrations.AlterField(
            model_name="brandtheme",
            name="account",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="brand_themes",
                to="user.account",
                help_text="Account that owns the theme.",
            ),
        ),
        # Remove old constraints
        migrations.RemoveConstraint(
            model_name="brandtheme",
            name="uq_brand_professional_name",
        ),
        migrations.RemoveConstraint(
            model_name="brandtheme",
            name="uq_brand_professional_active",
        ),
        # Add new constraints for account
        migrations.AddConstraint(
            model_name="brandtheme",
            constraint=models.UniqueConstraint(
                fields=["account", "name"],
                name="uq_brand_account_name",
            ),
        ),
        migrations.AddConstraint(
            model_name="brandtheme",
            constraint=models.UniqueConstraint(
                fields=["account"],
                condition=models.Q(is_active=True),
                name="uq_brand_account_active",
            ),
        ),
        # Remove old indexes
        migrations.RemoveIndex(
            model_name="brandtheme",
            name="ix_brand_professional_active",
        ),
        migrations.RemoveIndex(
            model_name="brandtheme",
            name="ix_brand_professional",
        ),
        # Add new indexes for account
        migrations.AddIndex(
            model_name="brandtheme",
            index=models.Index(fields=["account", "is_active"], name="ix_brand_account_active"),
        ),
        migrations.AddIndex(
            model_name="brandtheme",
            index=models.Index(fields=["account"], name="ix_brand_account"),
        ),
        # Drop professional field
        migrations.RemoveField(
            model_name="brandtheme",
            name="professional",
        ),
    ]
