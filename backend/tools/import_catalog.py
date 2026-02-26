"""
@Deprecated
Importe Areas + Prestations depuis backend/tools/areas.csv et prestations.csv.

Lancer :
    python backend/tools/import_catalog.py
# (Optionnel, si tu ajoutes un fichier vide backend/__init__.py)
#   python -m backend.tools.import_catalog
"""

from __future__ import annotations

import csv
import os
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

_TWO_PLACES = Decimal("0.01")

# --- Localisation des CSV (dans le même dossier que ce script) ---
SCRIPT_DIR = Path(__file__).resolve().parent
AREAS_CSV = SCRIPT_DIR / "areas.csv"
PRESTAS_CSV = SCRIPT_DIR / "prestations.csv"

# Assure que <repo>/backend est dans le PYTHONPATH (utile en mode script standalone)
BACKEND_DIR = SCRIPT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Bootstrap Django si pas encore initialisé (mode script standalone)
import django  # noqa: E402

if not django.apps.registry.apps.ready:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

from apps.catalog.models import Area, Prestation, PrestationStatus  # noqa: E402


def euros_to_cents_local(value: Decimal | str | float | int) -> int:
    """
    Convertit des euros (Decimal/str/float/int) -> centimes (int),
    arrondi HALF_UP à 2 décimales.
    """
    d = value if isinstance(value, Decimal) else Decimal(str(value))
    q = d.quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)
    return int(q * 100)


def _read_csv(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"CSV introuvable: {path}")
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    cleaned = []
    for row in rows:
        new_row = {}
        for k, v in row.items():
            kk = (k or "").replace("\ufeff", "").strip()  # enlève BOM + trim
            new_row[kk] = v
        cleaned.append(new_row)
    return cleaned


def _norm(s: str | None) -> str:
    return (s or "").strip()


def import_areas(rows: list[dict]) -> dict[str, Area]:
    """
    Accepte colonnes:
      - "key" (optionnelle)
      - "name" (obligatoire)
    Retourne un mapping key->Area (clé en lowercase),
    sinon name->Area (name en lowercase).
    """
    mapping: dict[str, Area] = {}
    for row in rows:
        key = _norm(row.get("key")).lower()
        name = _norm(row.get("name"))
        if not name:
            raise ValueError(f"Area invalide (name manquant): {row}")
        area, _ = Area.objects.get_or_create(name=name)
        mapping[(key or name.lower())] = area
    return mapping


def parse_rate_cents(row: dict) -> int:
    """
    Gère soit 'default_rate_cents' directement, soit 'default_rate_eur'.
    """
    cents_raw = _norm(row.get("default_rate_cents"))
    if cents_raw:
        try:
            return int(cents_raw)
        except ValueError:
            raise ValueError(f"default_rate_cents invalide: {cents_raw}")

    eur_raw = _norm(row.get("default_rate_eur"))
    if eur_raw:
        try:
            return euros_to_cents_local(Decimal(eur_raw))
        except Exception as exc:
            raise ValueError(f"default_rate_eur invalide: {eur_raw}") from exc

    return 0


def resolve_area(row: dict, areas_map: dict[str, Area]) -> Area:
    """
    Essaye dans l'ordre: area_key (lowercase), area_name/area (lookup i/regex).
    """
    area_key = _norm(row.get("area_key")).lower()
    area_name = _norm(row.get("area_name")) or _norm(row.get("area"))

    if area_key and area_key in areas_map:
        return areas_map[area_key]

    if area_name:
        # Essaye insensible à la casse
        from django.db.models import Q

        area = Area.objects.filter(Q(name__iexact=area_name)).first()
        if area:
            return area
        # Sinon on la crée
        area, _ = Area.objects.get_or_create(name=area_name)
        return area

    raise ValueError(f"Impossible de résoudre l'Area pour la prestation: {row}")


def import_prestations(rows: list[dict], areas_map: dict[str, Area]) -> tuple[int, int, int]:
    """
    Colonnes tolérées:
      - area_key (ou area_name / area)
      - name (obligatoire)
      - description
      - weight_days (sinon 0)
      - default_rate_eur OU default_rate_cents
      - status (DRAFT/ACTIVE/ARCHIVED) — insensible à la casse

    Retourne: (created, updated, archived)
    """
    created = 0
    updated = 0
    archived = 0
    seen_keys = set()

    for row in rows:
        name = _norm(row.get("name"))
        if not name:
            raise ValueError(f"Prestation invalide (name manquant): {row}")

        area = resolve_area(row, areas_map)
        key = (area.id, name.lower())
        seen_keys.add(key)

        description = _norm(row.get("description"))
        weight_days_raw = _norm(row.get("weight_days"))
        try:
            weight_days = int(weight_days_raw) if weight_days_raw else 0
        except ValueError:
            raise ValueError(f"weight_days invalide: {weight_days_raw}")

        default_rate_cents = parse_rate_cents(row)

        status_raw = _norm(row.get("status")).upper() or "DRAFT"
        if status_raw not in PrestationStatus.values:
            raise ValueError(f"Statut inconnu: {status_raw}")

        _, is_created = Prestation.objects.update_or_create(
            area=area,
            name=name,
            defaults={
                "description": description,
                "weight_days": weight_days,
                "default_rate_cents": default_rate_cents,
                "status": status_raw,
            },
        )
        created += int(is_created)
        updated += int(not is_created)

    # Archivage des prestations absentes du CSV
    for p in Prestation.objects.all():
        key = (p.area_id, p.name.lower())
        if key not in seen_keys and p.status != PrestationStatus.ARCHIVED:
            p.status = PrestationStatus.ARCHIVED
            p.save(update_fields=["status"])
            archived += 1

    return created, updated, archived


def main() -> None:
    print(f"Lecture: {AREAS_CSV}")
    areas_rows = _read_csv(AREAS_CSV)
    areas_map = import_areas(areas_rows)
    print(f"Areas importées: {len(areas_rows)}")

    print(f"Lecture: {PRESTAS_CSV}")
    presta_rows = _read_csv(PRESTAS_CSV)
    created, updated, archived = import_prestations(presta_rows, areas_map)
    print(f"Prestations — created={created}, updated={updated}, archived={archived}")
    print("Import OK ✅")


if __name__ == "__main__":
    main()
