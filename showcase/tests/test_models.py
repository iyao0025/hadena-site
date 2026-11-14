from django.test import TestCase

from showcase.models import ContactMessage


class ContactMessageModelTest(TestCase):
    def test_create_contact_message(self):
        msg = ContactMessage.objects.create(
            full_name="Kouamé Jean",
            company="Abidjan Tech Corp",
            email="jean.kouame@abidjantech.ci",
            phone="+225 07 09 779 787",
            service="securite",
            message="Besoin d'un audit de cybersécurité pour nos serveurs.",
            consent_gdpr=True,
            ip_address="127.0.0.1",
        )
        self.assertEqual(msg.full_name, "Kouamé Jean")
        self.assertEqual(msg.get_service_display(), "Sécurité informatique")
        self.assertTrue(msg.consent_gdpr)
        self.assertFalse(msg.is_processed)
        self.assertIn("Kouamé Jean", str(msg))
        self.assertIn("Sécurité informatique", str(msg))
