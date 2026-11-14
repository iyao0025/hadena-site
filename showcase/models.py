from django.db import models


class ContactMessage(models.Model):
    """Stockage persistant des demandes de devis et contacts avec traçabilité RGPD."""

    SERVICE_CHOICES = [
        ("gouvernance", "Management & Gouvernance IT"),
        ("reseaux", "Systèmes & Réseaux"),
        ("securite", "Sécurité informatique"),
        ("audit", "Audit informatique"),
        ("maintenance", "Service Desk & Maintenance"),
        ("data_bi", "Data Analytics & BI"),
        ("web_mobile", "Applications Web & Mobile"),
        ("agence_digitale", "Agence Web & Digitale"),
        ("sur_mesure", "Solutions sur mesure"),
        ("produits", "Matériels & Logiciels"),
        ("formation", "Formation professionnelle"),
        ("autre", "Autre demande"),
    ]

    full_name = models.CharField(max_length=150, verbose_name="Nom complet")
    company = models.CharField(max_length=150, blank=True, verbose_name="Entreprise")
    email = models.EmailField(verbose_name="E-mail")
    phone = models.CharField(max_length=30, verbose_name="Téléphone")
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES, verbose_name="Service concerné")
    message = models.TextField(verbose_name="Description du besoin")
    consent_gdpr = models.BooleanField(
        default=False,
        verbose_name="Consentement RGPD accordé",
        help_text="Consentement explicite au traitement des données personnelles",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Adresse IP",
        help_text="Pour protection anti-abus et conformité de sécurité",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de réception")
    is_processed = models.BooleanField(default=False, verbose_name="Traité")
    notes = models.TextField(blank=True, verbose_name="Notes internes")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact & devis"

    def __str__(self):
        return f"{self.full_name} ({self.get_service_display()}) - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

