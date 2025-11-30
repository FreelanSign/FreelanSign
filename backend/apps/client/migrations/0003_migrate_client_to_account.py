from django.db import migrations


def migrate_clients(apps, schema_editor):
    Client = apps.get_model("client", "Client")
    Account = apps.get_model("user", "Account")

    for client in Client.objects.all():
        account = Account.objects.filter(user=client.owner).first()
        if account:
            client.account = account
            client.save()


def reverse_migrate(apps, schema_editor):
    Client = apps.get_model("client", "Client")
    Client.objects.update(account=None)


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0002_client_account"),
    ]

    operations = [
        migrations.RunPython(migrate_clients, reverse_migrate),
    ]
