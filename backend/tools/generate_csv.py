#!/usr/bin/env python3
"""
Generate CSVs for areas and prestations from JSON sources located in ./jsons.

Usage (script mode):
  python generate_csv.py

Usage (as a module):
  from tool.generate_csv import generate_csv
  generate_csv()  # writes CSVs next to the script by default
  # or with a custom output directory:
  generate_csv(out_dir="path/to/out")
"""
import csv
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

VALID_STATUS = {"ACTIVE", "DRAFT", "ARCHIVED"}

# Encoding for CSV output. Default 'utf-8-sig' to make Excel happy.
OUTPUT_ENCODING = os.getenv("CSV_ENCODING", "utf-8-sig")


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_areas(areas: List[Dict]):
    keys = set()
    for i, a in enumerate(areas, start=1):
        if "key" not in a or "name" not in a:
            raise ValueError(f"[areas] Ligne {i}: champs requis manquants (key, name).")
        if not a["key"] or not a["name"]:
            raise ValueError(f"[areas] Ligne {i}: key/name vides.")
        if a["key"] in keys:
            raise ValueError(f"[areas] key en doublon: {a['key']}")
        keys.add(a["key"])
    return keys


def validate_prestations(prestations: List[Dict], area_keys: set):
    for i, p in enumerate(prestations, start=1):
        for field in ["area_key", "name", "description", "weight_days", "default_rate_eur", "status"]:
            if field not in p:
                raise ValueError(f"[prestations] Ligne {i}: champ manquant '{field}'.")
        if p["area_key"] not in area_keys:
            raise ValueError(f"[prestations] Ligne {i}: area_key inconnu '{p['area_key']}'")
        if not isinstance(p["weight_days"], int) or p["weight_days"] <= 0:
            raise ValueError(f"[prestations] Ligne {i}: weight_days doit être un entier > 0.")
        if not isinstance(p["default_rate_eur"], int) or p["default_rate_eur"] < 0:
            raise ValueError(f"[prestations] Ligne {i}: default_rate_eur doit être un entier (centimes) >= 0.")
        if p["status"] not in VALID_STATUS:
            raise ValueError(f"[prestations] Ligne {i}: status invalide '{p['status']}', attendu {VALID_STATUS}.")


def write_areas_csv(areas: List[Dict], out_path: Path):
    with open(out_path, "w", encoding=OUTPUT_ENCODING, newline="") as f:
        w = csv.DictWriter(f, fieldnames=["key", "name"])
        w.writeheader()
        for a in areas:
            w.writerow({"key": a["key"], "name": a["name"]})


def write_prestations_csv(prestations: List[Dict], out_path: Path):
    with open(out_path, "w", encoding=OUTPUT_ENCODING, newline="") as f:
        w = csv.DictWriter(f, fieldnames=["area_key", "name", "description", "weight_days", "default_rate_eur", "status"])
        w.writeheader()
        for p in prestations:
            w.writerow(
                {
                    "area_key": p["area_key"],
                    "name": p["name"],
                    "description": p["description"],
                    "weight_days": p["weight_days"],
                    "default_rate_eur": p["default_rate_eur"],
                    "status": p["status"],
                }
            )


def generate_csv(out_dir: Optional[Path] = None) -> Path:
    """
    Génère areas.csv et prestations.csv.
    - Lit les JSON depuis: <script_dir>/jsons/areas.json & jsons/prestations.json
    - Écrit les CSV dans: out_dir (par défaut <script_dir>)
    Retourne le chemin absolu du dossier de sortie.
    """
    script_dir = Path(__file__).resolve().parent
    json_dir = script_dir / "jsons"
    areas_json = json_dir / "areas.json"
    prestations_json = json_dir / "prestations.json"

    if not areas_json.exists():
        raise FileNotFoundError(f"Fichier introuvable: {areas_json}")
    if not prestations_json.exists():
        raise FileNotFoundError(f"Fichier introuvable: {prestations_json}")

    out_dir = Path(out_dir) if out_dir else script_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    areas = load_json(areas_json)
    prestations = load_json(prestations_json)

    area_keys = validate_areas(areas)
    validate_prestations(prestations, area_keys)

    write_areas_csv(areas, out_dir / "areas.csv")
    write_prestations_csv(prestations, out_dir / "prestations.csv")

    print(f"OK ✅ CSV générés dans: {out_dir.resolve()}")
    print(" - areas.csv (colonnes: key,name)")
    print(" - prestations.csv (colonnes: area_key,name,description,weight_days,default_rate_eur,status)")
    return out_dir.resolve()


if __name__ == "__main__":
    try:
        generate_csv()
    except Exception as e:
        print(f"Erreur ❌: {e}", file=sys.stderr)
        sys.exit(1)
