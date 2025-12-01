# Generated migration for Phase 5.3 - Data migration
from django.db import migrations


def migrate_professional_to_account(apps, schema_editor):
    """Migrate BrandTheme.professional (User) to BrandTheme.account (Account)."""
    BrandTheme = apps.get_model("branding", "BrandTheme")
    Account = apps.get_model("user", "Account")
    
    for theme in BrandTheme.objects.select_related("professional").all():
        # Get the first account for this user
        account = Account.objects.filter(user=theme.professional).first()
        if account:
            theme.account = account
            theme.save(update_fields=["account"])
        else:
            # Log warning but don't fail - will be handled in cleanup phase
            print(f"Warning: User {theme.professional.id} has no account, theme {theme.id} not migrated")


class Migration(migrations.Migration):

    dependencies = [
        ("branding", "0002_add_account_fk"),
        ("user", "0010_migrate_professional_to_account"),
    ]

    operations = [
        migrations.RunPython(
            migrate_professional_to_account,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
