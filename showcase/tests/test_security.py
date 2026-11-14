from django.test import Client, TestCase
from django.urls import reverse


class SecurityHeadersTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_security_headers_present(self):
        response = self.client.get(reverse("showcase:home"))
        # Content Security Policy (CSP)
        self.assertIn("Content-Security-Policy", response.headers)
        csp = response.headers["Content-Security-Policy"]
        self.assertIn("default-src 'self'", csp)
        self.assertIn("frame-ancestors 'none'", csp)

        # OWASP headers
        self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(response.headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(response.headers.get("Referrer-Policy"), "strict-origin-when-cross-origin")
        self.assertEqual(response.headers.get("X-XSS-Protection"), "1; mode=block")

    def test_cookie_consent_flow(self):
        # 1. Avant consentement : la bannière est affichée
        res1 = self.client.get(reverse("showcase:home"))
        self.assertContains(res1, "cookie-consent-banner")

        # 2. Envoi du consentement
        post_res = self.client.post(reverse("showcase:set_cookie_consent"), data={"consent": "accepted"})
        self.assertEqual(post_res.status_code, 302)
        self.assertIn("hadena_cookie_consent", post_res.cookies)
        self.assertEqual(post_res.cookies["hadena_cookie_consent"].value, "accepted")

        # 3. Après consentement : la bannière n'apparaît plus
        self.client.cookies["hadena_cookie_consent"] = "accepted"
        res2 = self.client.get(reverse("showcase:home"))
        self.assertNotContains(res2, "cookie-consent-banner")
