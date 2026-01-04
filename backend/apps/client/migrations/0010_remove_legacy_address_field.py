# Generated manually on 2026-01-04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0009_migrate_address_data"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="client",
            name="address",
        ),
    ]
