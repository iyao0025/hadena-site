from django.test import TestCase

from showcase.forms import ContactForm


class ContactFormTest(TestCase):
    def test_valid_form(self):
        data = {
            "full_name": "Awa Touré",
            "company": "Ivoire Logistics",
            "email": "awa.toure@ivoirelogistics.ci",
            "phone": "+225 05 85 03 16 16",
            "service": "gouvernance",
            "message": "Demande d'accompagnement pour schéma directeur informatique.",
            "consent_gdpr": True,
            "website": "",  # honeypot vide
        }
        form = ContactForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_honeypot_spam_rejection(self):
        data = {
            "full_name": "Spammer Bot",
            "company": "Fake Corp",
            "email": "bot@spam.com",
            "phone": "+225 01 02 03 04 05",
            "service": "reseaux",
            "message": "Achetez nos liens",
            "consent_gdpr": True,
            "website": "http://spam-link.com",  # Honeypot rempli par le bot
        }
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("website", form.errors)

    def test_gdpr_consent_required(self):
        data = {
            "full_name": "Konan Michel",
            "company": "Finance Plus",
            "email": "konan@financeplus.ci",
            "phone": "+225 07 09 77 97 87",
            "service": "audit",
            "message": "Demande d'audit.",
            "consent_gdpr": False,  # Non consenti
            "website": "",
        }
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("consent_gdpr", form.errors)

    def test_invalid_short_phone(self):
        data = {
            "full_name": "Konan Michel",
            "email": "konan@test.ci",
            "phone": "123",  # Trop court
            "service": "audit",
            "message": "Test",
            "consent_gdpr": True,
            "website": "",
        }
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)
