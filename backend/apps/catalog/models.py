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
    custom = models.BooleanField(
        _("Custom"),
        default=False,
        help_text="Indique si la prestation a été ajoutée par un professionel (non partagée globalement).",
        db_index=True,
    )
    professional_user = models.ForeignKey(
        "user.ProfessionalUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="custom_prestations",
        help_text=_("If set, indicates which professional created this custom prestation."),
    )

    class Meta:
        verbose_name = _("Prestation")
        verbose_name_plural = _("Prestations")
        ordering = ("area__name", "name")
        constraints = [
            # 1) Contrainte globale : area+name unique uniquement pour prestations globales (professional_user IS NULL)
            models.UniqueConstraint(
                fields=["area", "name"],
                condition=models.Q(professional_user__isnull=True),
                name="unique_area_prestation_name_global",
            ),
            # 2) Contrainte par pro : un pro ne peut pas créer deux prestations de même nom (au niveau pro)
            models.UniqueConstraint(
                fields=["professional_user", "name"],
                condition=models.Q(professional_user__isnull=False),
                name="unique_professional_prestation_name",
            ),
            models.CheckConstraint(check=models.Q(weight_days__gte=0), name="prestation_weight_days_nonneg"),
            models.CheckConstraint(check=models.Q(default_rate_cents__gte=0), name="prestation_rate_nonneg"),
        ]
        indexes = [
            models.Index(fields=["area", "status"], name="idx_prest_area_status"),
            models.Index(fields=["professional_user"], name="idx_prest_professional_user"),
        ]

    def __str__(self):
        return f"{self.area.name} - {self.name}"

    # helpers côté code/business
    @property
    def default_rate_eur(self) -> float:
        return cents_to_euros(self.default_rate_cents)

    def set_default_rate_eur(self, euros_decimal):
        self.default_rate_cents = euros_to_cents(euros_decimal)
