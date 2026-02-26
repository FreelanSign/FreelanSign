"""
Management command : importe Areas + Prestations depuis tools/jsons/ vers la DB.

Usage:
    python manage.py import_catalog
    python manage.py import_catalog --dry-run
"""

from django.core.management.base import BaseCommand

from tools.generate_csv import generate_csv
from tools.import_catalog import _read_csv, import_areas, import_prestations


class Command(BaseCommand):
    help = "Import areas + prestations depuis tools/jsons/ vers la DB"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Génère les CSV sans toucher à la base de données",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        self.stdout.write("Génération des CSV depuis tools/jsons/...")
        out_dir = generate_csv()

        if dry_run:
            self.stdout.write(self.style.WARNING("--dry-run : CSV générés, import DB ignoré."))
            return

        areas_rows = _read_csv(out_dir / "areas.csv")
        areas_map = import_areas(areas_rows)
        self.stdout.write(f"  Areas importées : {len(areas_map)}")

        presta_rows = _read_csv(out_dir / "prestations.csv")
        created, updated, archived = import_prestations(presta_rows, areas_map)
        self.stdout.write(f"  Prestations — created={created}, updated={updated}, archived={archived}")

        self.stdout.write(self.style.SUCCESS("Import OK ✅"))
