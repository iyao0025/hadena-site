class SecurityHeadersMiddleware:
    """Middleware pour appliquer les en-têtes de sécurité conformes aux normes OWASP et CSP."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Content Security Policy (CSP)
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net",
            "font-src 'self' https://fonts.gstatic.com data:",
            "img-src 'self' data: https:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
        response["Content-Security-Policy"] = "; ".join(csp_directives)

        # En-têtes OWASP Top 10
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response["X-XSS-Protection"] = "1; mode=block"

        return response


class CookieConsentMiddleware:
    """Middleware de gestion du consentement cookies (RGPD)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Statut du consentement : 'accepted', 'rejected' ou None (non défini)
        request.cookie_consent = request.COOKIES.get("hadena_cookie_consent")
        return self.get_response(request)

