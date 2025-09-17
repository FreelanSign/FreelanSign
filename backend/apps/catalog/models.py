from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import SoftDeleteModel, TimestampedModel
from apps.core.utils.money import cents_to_euros, euros_to_cents


class Area(TimestampedModel):
    name = models.CharField(_("Nom de l'area"), max_length=120, unique=True)

    class Meta:
        verbose_name = _("Area")
        verbose_name_plural = _("Areas")
        ordering = ("name",)

    def __str__(self):
        return self.name


class PrestationStatus(models.TextChoices):
    DRAFT = "DRAFT", _("Brouillon")
    ACTIVE = "ACTIVE", _("Active")
    ARCHIVED = "ARCHIVED", _("Archivée")


class Prestation(TimestampedModel, SoftDeleteModel):
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name="prestations")
    name = models.CharField(_("Nom de la prestation"), max_length=120)
    description = models.TextField(_("Description de la prestation"), blank=True)
    weight_days = models.PositiveIntegerField(
        _("Jours-homme moyens (entier)"),
        help_text=_("Durée moyenne en jours pour exécuter la prestation."),
        default=1,
    )
    default_rate_cents = models.BigIntegerField(
        _("Tariff unique par prestation (en centimes)"),
        help_text=_("Exemple: 120000 pour 1200.00€"),
        default=0,
    )
    status = models.CharField(
        _("Statut de la prestation"),
        max_length=20,
        choices=PrestationStatus.choices,
        default=PrestationStatus.DRAFT,
        db_index=True,
    )

    class Meta:
        verbose_name = _("Prestation")
        verbose_name_plural = _("Prestations")
        ordering = ("area__name", "name")
        constraints = [
            models.UniqueConstraint(fields=["area", "name"], name="unique_area_prestation_name"),
            models.CheckConstraint(check=models.Q(weight_days__gte=0), name="prestation_weight_days_nonneg"),
            models.CheckConstraint(check=models.Q(default_rate_cents__gte=0), name="prestation_rate_nonneg"),
        ]
        indexes = [
            models.Index(fields=["area", "status"], name="idx_prest_area_status"),
        ]

    def __str__(self):
        return f"{self.area.name} - {self.name}"

    # helpers côté code/business
    @property
    def default_rate_eur(self) -> float:
        return cents_to_euros(self.default_rate_cents)

    def set_default_rate_eur(self, euros_decimal):
        self.default_rate_cents = euros_to_cents(euros_decimal)
