# apps/client/signals.py
"""
Signals for Client model.

RGPD compliance: Prevent soft delete of Client if active Quotes exist.
"""

from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.client.models import Client


@receiver(pre_save, sender=Client)
def prevent_soft_delete_with_quotes(sender, instance, **kwargs):
    """
    Bloque le soft delete d'un Client si des Quotes ACTIVES existent.

    Statuts actifs : DRAFT, SENT, ACCEPTED (activité en cours)
    Statuts terminés : PAID, CANCELLED, EXPIRED, REJECTED (conservation légale, anonymisation possible)

    AIDEV-NOTE: Ce signal utilise la méthode commune de vérification de l'état précédent
    en récupérant l'objet old depuis la DB. Sensible aux race conditions mais accepté
    pour la simplicité (risque faible en pratique).

    Raises:
        ValueError: Si le Client a des Quotes actives
    """
    if instance.pk and instance.is_deleted:
        try:
            # Récupérer l'état précédent depuis la DB
            old = Client.all_objects.get(pk=instance.pk)
            if not old.is_deleted:
                # Importation locale pour éviter dépendance circulaire
                from apps.quote.models import Quote

                # AIDEV-NOTE: Vérifier uniquement les statuts actifs
                # PAID est exclu car c'est une transaction terminée
                active_statuses = ["DRAFT", "SENT", "ACCEPTED"]
                if Quote.objects.filter(client=instance, status__in=active_statuses).exists():
                    raise ValueError(
                        "Impossible de supprimer le client : des devis actifs existent. "
                        "Veuillez d'abord finaliser ou annuler les devis en cours."
                    )
        except Client.DoesNotExist:
            # Client n'existe pas encore (création), pas de vérification nécessaire
            pass
