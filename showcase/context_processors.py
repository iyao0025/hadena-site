from datetime import datetime


def site_settings(request):
    """Context processor fournissant les coordonnées et paramètres globaux à tous les gabarits."""
    return {
        "COMPANY_NAME": "Hadena Limited",
        "COMPANY_TAGLINE": "Un monde au potentiel illimité",
        "MANAGER_NAME": "Aurore AGNERO",
        "MANAGER_ROLE": "Gérante",
        "CONTACT_EMAIL": "info@hadena-limited.com",
        "CONTACT_PHONE_PRIMARY": "+225 07 09 779 787",
        "CONTACT_PHONE_SECONDARY": "+225 05 85 03 16 16",
        "CONTACT_ADDRESS": "Cocody Washington, Abidjan – Côte d'Ivoire",
        "BUSINESS_HOURS": "Lun - Ven : 8h00 - 18h00",
        "FACEBOOK_URL": "https://www.facebook.com/hadena.limited",
        "LINKEDIN_URL": "https://www.linkedin.com/company/hadena-limited",
        "CURRENT_YEAR": datetime.now().year,
        "COOKIE_CONSENT": getattr(request, "cookie_consent", None),
    }

