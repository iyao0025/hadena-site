from django.test import Client, TestCase
from django.urls import reverse

from showcase.models import ContactMessage


class ShowcaseViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_status_and_content(self):
        url = reverse("showcase:home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "HADENA LIMITED")
        self.assertContains(response, "Des systèmes d'information")
        self.assertContains(response, "Management & Gouvernance IT")
        self.assertContains(response, "Systèmes & Réseaux")
        self.assertContains(response, "Sécurité informatique")
        self.assertContains(response, "Quartz SA")
        self.assertContains(response, "Innovation")
        self.assertContains(response, "Notre méthode")
        self.assertContains(response, "Parler à un expert")
        self.assertContains(response, "Découvrir nos services")
        self.assertContains(response, "Questions fréquentes")

    def test_home_page_contact_submission(self):
        url = reverse("showcase:home")
        data = {
            "full_name": "Bakary Diarra",
            "company": "Agro Babi",
            "email": "b.diarra@agrobabi.ci",
            "phone": "+225 07 11 22 33 44",
            "service": "data_bi",
            "message": "Mise en place de dashboards décisionnels sous Power BI.",
            "consent_gdpr": True,
            "website": "",
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ContactMessage.objects.filter(email="b.diarra@agrobabi.ci").exists())
        self.assertContains(response, "Merci pour votre message")

    def test_about_page(self):
        response = self.client.get(reverse("showcase:about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Qui sommes-nous ?")
        self.assertContains(response, "Le mot de la gérante")
        self.assertContains(response, "Aurore AGNERO")
        self.assertIn("references", response.context)
        self.assertTrue(len(response.context["references"]) > 0)
        self.assertContains(response, "Ils nous ont fait confiance")

    def test_services_catalog_page(self):
        response = self.client.get(reverse("showcase:services"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Des Services IT")
        self.assertContains(response, "de Bout en Bout")

    def test_service_detail_page(self):
        response = self.client.get(reverse("showcase:service_detail", kwargs={"slug": "management-gouvernance-it"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Management &amp; Gouvernance IT")

    def test_products_page(self):
        response = self.client.get(reverse("showcase:products"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Matériels")
        self.assertContains(response, "Professionnels Certifiés")

    def test_training_page(self):
        response = self.client.get(reverse("showcase:training"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Formations Pratiques")
        self.assertContains(response, "Certifiantes")

    def test_contact_page(self):
        response = self.client.get(reverse("showcase:contact"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Contactez")
        self.assertContains(response, "nos Experts IT")

    def test_legal_and_privacy_pages(self):
        resp_leg = self.client.get(reverse("showcase:mentions_legales"))
        self.assertEqual(resp_leg.status_code, 200)
        self.assertContains(resp_leg, "Mentions Légales")

        resp_priv = self.client.get(reverse("showcase:privacy"))
        self.assertEqual(resp_priv.status_code, 200)
        self.assertContains(resp_priv, "Politique de Confidentialité")
        self.assertContains(resp_priv, "RGPD")

    def test_robots_txt(self):
        response = self.client.get("/robots.txt")
        self.assertEqual(response.status_code, 200)
        self.assertIn("User-agent: *", response.content.decode())
        self.assertIn("Sitemap:", response.content.decode())

    def test_sitemap_xml(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertIn("<urlset", response.content.decode())

    def test_cookie_consent_get_and_post(self):
        # Test GET
        url = reverse("showcase:set_cookie_consent")
        resp_get = self.client.get(f"{url}?consent=accepted", HTTP_REFERER="/")
        self.assertEqual(resp_get.status_code, 302)
        self.assertEqual(resp_get.cookies.get("hadena_cookie_consent").value, "accepted")

        # Test POST
        resp_post = self.client.post(url, data={"consent": "rejected"}, HTTP_REFERER="/qui-sommes-nous/")
        self.assertEqual(resp_post.status_code, 302)
        self.assertEqual(resp_post.cookies.get("hadena_cookie_consent").value, "rejected")

        # Test AJAX
        resp_ajax = self.client.get(f"{url}?consent=accepted", headers={"x-requested-with": "XMLHttpRequest"})
        self.assertEqual(resp_ajax.status_code, 200)
        self.assertEqual(resp_ajax.json(), {"status": "ok", "consent": "accepted"})
