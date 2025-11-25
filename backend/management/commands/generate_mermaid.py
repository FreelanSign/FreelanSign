# generate_mermaid.py
import os

from django.apps import apps
from django.db import models


def generate_entity_diagram():
    """Génère un diagramme entité-relation Mermaid depuis les modèles Django"""

    mermaid = ["erDiagram"]

    # Parcourir tous les modèles
    for model in apps.get_models():
        model_name = model.__name__

        # Parcourir les champs du modèle
        for field in model._meta.get_fields():
            if isinstance(field, models.ForeignKey):
                related_model = field.related_model.__name__
                mermaid.append(f'    {model_name} ||--o{{ {related_model} : "{field.name}"')

            elif isinstance(field, models.OneToOneField):
                related_model = field.related_model.__name__
                mermaid.append(f'    {model_name} ||--|| {related_model} : "{field.name}"')

            elif isinstance(field, models.ManyToManyField):
                related_model = field.related_model.__name__
                mermaid.append(f'    {model_name} }}o--o{{ {related_model} : "{field.name}"')

    return "\n".join(mermaid)


# Utilisation dans un management command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Génère un diagramme Mermaid des entités Django"

    def handle(self, *args, **options):
        diagram = generate_entity_diagram()

        # Sauvegarder dans le dossier courant
        current_dir = os.getcwd()
        output_path = os.path.join(current_dir, "entity_diagram.mermaid")

        with open(output_path, "w") as f:
            f.write(diagram)

        self.stdout.write(self.style.SUCCESS(f"Diagramme généré avec succès dans : {output_path}"))
        print(diagram)
