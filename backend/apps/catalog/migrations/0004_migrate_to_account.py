# Generated migration for Phase 5.4 - Data migration
from django.db import migrations


def migrate_professional_user_to_account(apps, schema_editor):
    """Migrate Prestation.professional_user (ProfessionalUser) to Prestation.account (Account)."""
    Prestation = apps.get_model("catalog", "Prestation")
    Account = apps.get_model("user", "Account")
    
    # Only migrate custom prestations (those with professional_user set)
    for prestation in Prestation.objects.select_related("professional_user").filter(
        professional_user__isnull=False
    ):
        # Get the user from ProfessionalUser, then find their account
        user = prestation.professional_user.user
        account = Account.objects.filter(user=user).first()
        
        if account:
            prestation.account = account
            prestation.save(update_fields=["account"])
        else:
            # Log warning but don't fail
            print(f"Warning: User {user.id} has no account, prestation {prestation.id} not migrated")


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_add_account_fk"),
        ("user", "0010_migrate_professional_to_account"),
    ]

    operations = [
        migrations.RunPython(
            migrate_professional_user_to_account,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
