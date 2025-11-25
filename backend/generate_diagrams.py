# generate_diagrams.py
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.apps import apps
from django.db import models


def get_field_type(field):
    """Retourne le type de champ en format lisible"""
    field_type = field.get_internal_type()
    type_map = {
        "CharField": "String",
        "TextField": "String",
        "IntegerField": "Number",
        "BigIntegerField": "Number",
        "PositiveIntegerField": "Number",
        "BooleanField": "Boolean",
        "DateField": "Date",
        "DateTimeField": "DateTime",
        "DecimalField": "Decimal",
        "FloatField": "Float",
        "EmailField": "String",
        "UUIDField": "UUID",
        "JSONField": "JSON",
        "URLField": "String",
    }
    return type_map.get(field_type, "String")


def get_relation_label(field):
    """Génère un label pour la relation"""
    return field.name


def generate_app_diagram(app_label):
    """Génère un class diagram Mermaid pour une app"""
    app_models = [m for m in apps.get_models() if m._meta.app_label == app_label]

    if not app_models:
        return None

    mermaid = ["classDiagram"]

    # Générer les classes avec leurs attributs
    for model in app_models:
        model_name = model.__name__
        mermaid.append(f"    class {model_name} {{")

        for field in model._meta.get_fields():
            # Ignorer les relations inverses
            if field.auto_created and not field.concrete:
                continue

            # Ignorer les relations pour les attributs (on les met après)
            if isinstance(field, (models.ForeignKey, models.OneToOneField, models.ManyToManyField)):
                continue

            field_name = field.name
            field_type = get_field_type(field)

            mermaid.append(f"        +{field_type} {field_name}")

        mermaid.append("    }")

    # Générer les relations
    for model in app_models:
        model_name = model.__name__

        for field in model._meta.get_fields():
            if isinstance(field, models.ForeignKey):
                related_model = field.related_model.__name__
                label = get_relation_label(field)
                # Many-to-one
                mermaid.append(f'    {model_name} "*" --> "1" {related_model} : {label}')

            elif isinstance(field, models.OneToOneField):
                related_model = field.related_model.__name__
                label = get_relation_label(field)
                # One-to-one
                mermaid.append(f'    {model_name} "1" --> "1" {related_model} : {label}')

            elif isinstance(field, models.ManyToManyField):
                # Éviter les doublons
                if hasattr(field.remote_field, "through") and field.remote_field.through._meta.auto_created:
                    related_model = field.related_model.__name__
                    label = get_relation_label(field)
                    # Many-to-many
                    mermaid.append(f'    {model_name} "*" --> "*" {related_model} : {label}')

    return "\n".join(mermaid)


def generate_all_diagrams():
    """Génère un diagramme pour chaque app"""
    app_labels = ["branding", "catalog", "client", "core", "email", "quote", "user"]

    os.makedirs("diagrams", exist_ok=True)

    for app_label in app_labels:
        print(f"Génération du diagramme pour {app_label}...")
        diagram = generate_app_diagram(app_label)

        if diagram:
            filename = f"diagrams/{app_label}_diagram.mermaid"
            with open(filename, "w") as f:
                f.write(diagram)
            print(f"  ✅ {filename}")
        else:
            print(f"  ⚠️  Aucun modèle trouvé pour {app_label}")

    print(f"\n🎉 Tous les diagrammes ont été générés dans le dossier 'diagrams/'")


if __name__ == "__main__":
    generate_all_diagrams()
