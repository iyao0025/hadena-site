from django.urls import path

from . import views

app_name = "showcase"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("qui-sommes-nous/", views.AboutView.as_view(), name="about"),
    path("services/", views.ServicesView.as_view(), name="services"),
    path("services/<slug:slug>/", views.ServiceDetailView.as_view(), name="service_detail"),
    path("produits/", views.ProductsView.as_view(), name="products"),
    path("formation/", views.TrainingView.as_view(), name="training"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("set-cookie-consent/", views.SetCookieConsentView.as_view(), name="set_cookie_consent"),
    path("mentions-legales/", views.MentionsLegalesView.as_view(), name="mentions_legales"),
    path("politique-de-confidentialite/", views.PrivacyPolicyView.as_view(), name="privacy"),
]
