import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .forms import ContactForm

logger = logging.getLogger(__name__)

# Données structurées conformes au document de travail Contenu_Site_Hadena_Limited.docx
SERVICES_CATALOG = [
    {
        "id": "gouvernance",
        "slug": "management-gouvernance-it",
        "title": "Management & Gouvernance IT",
        "short_desc": "Schéma directeur, pilotage de projets, alignement de l'IT sur vos objectifs métier selon les bonnes pratiques ITIL.",
        "icon": "compass",
        "image": "gouvernance.webp",
        "is_highlight": True,
        "full_desc": "La gouvernance des systèmes d'information consiste à s'assurer que vos investissements informatiques créent une réelle valeur pour votre entreprise. Nous vous accompagnons dans l'élaboration de schémas directeurs, le pilotage de vos projets et la mise en conformité réglementaire.",
        "deliverables": [
            "Diagnostic et cartographie du système d'information existant",
            "Élaboration du schéma directeur informatique aligné sur la stratégie d'entreprise",
            "Mise en place de politiques de gouvernance et bonnes pratiques ITIL",
            "Gestion de portefeuille de projets et assistance à maîtrise d'ouvrage (AMOA)",
        ],
    },
    {
        "id": "reseaux",
        "slug": "systemes-reseaux",
        "title": "Systèmes & Réseaux",
        "short_desc": "Conception, déploiement et administration de serveurs, réseaux, environnements cloud et solutions d'hébergement.",
        "icon": "server",
        "image": "reseaux.webp",
        "is_highlight": False,
        "full_desc": "Une infrastructure réseau performante et résiliente est l'épine dorsale de votre entreprise. Hadena Limited conçoit, déploie et supervise vos architectures locales, hybrides ou cloud pour garantir une disponibilité maximale.",
        "deliverables": [
            "Architecture et câblage réseau haute disponibilité (LAN, WAN, Wi-Fi pro)",
            "Virtualisation et administration des serveurs (Windows Server, Linux)",
            "Migration et hébergement cloud (IaaS, PaaS, solutions de messagerie)",
            "Supervision 24/7 et monitoring proactif des équipements",
        ],
    },
    {
        "id": "securite",
        "slug": "securite-informatique",
        "title": "Sécurité informatique",
        "short_desc": "Analyse des risques, durcissement des systèmes, sauvegardes et plans de continuité pour protéger vos données.",
        "icon": "shield-check",
        "image": "securite.webp",
        "is_highlight": False,
        "full_desc": "Face à la recrudescence des cybermenaces, protéger vos actifs numériques est un impératif vital. Nous mettons en œuvre une protection à 360° pour vos postes, réseaux, serveurs et données sensibles.",
        "deliverables": [
            "Sécurisation périmétrique (pare-feu nouvelle génération, VPN, segmentation)",
            "Protection des postes de travail et serveurs (antivirus managé, EDR)",
            "Stratégie de sauvegarde 3-2-1 immuable et plans de reprise d'activité (PRA)",
            "Sensibilisation des collaborateurs aux risques de phishing et ingénierie sociale",
        ],
    },
    {
        "id": "audit",
        "slug": "audit-informatique",
        "title": "Audit informatique",
        "short_desc": "État des lieux objectif de votre parc, de vos processus et de votre sécurité, avec un plan d'actions priorisé.",
        "icon": "file-search",
        "image": "audit.webp",
        "is_highlight": False,
        "full_desc": "L'audit vous apporte une vision claire et indépendante sur la maturité de votre système d'information, ses faiblesses cachées et les opportunités d'optimisation budgétaire.",
        "deliverables": [
            "Inventaire exhaustif matériel, logiciel et licences",
            "Audit de vulnérabilité et tests d'intrusion techniques",
            "Évaluation de la conformité aux normes et réglementations locales",
            "Rapport synthétique pour la direction avec plan de remédiation priorisé",
        ],
    },
    {
        "id": "maintenance",
        "slug": "service-desk-maintenance",
        "title": "Service Desk & Maintenance",
        "short_desc": "Support utilisateurs, maintenance préventive et curative de vos équipements, suivi des incidents.",
        "icon": "headset",
        "image": "maintenance.webp",
        "is_highlight": False,
        "full_desc": "Offrez à vos équipes un guichet unique d'assistance technique réactif pour résoudre immédiatement les pannes, maintenir le matériel opérationnel et éviter toute perte de productivité.",
        "deliverables": [
            "Support technique multi-canal (téléphone, e-mail, téléassistance)",
            "Maintenance préventive programmée sur site et dépannage curatif d'urgence",
            "Gestion de parc et renouvellement anticipé des matériels",
            "Accords de niveau de service (SLA) avec engagement de temps de résolution",
        ],
    },
    {
        "id": "data_bi",
        "slug": "data-analytics-bi",
        "title": "Data Analytics & BI",
        "short_desc": "Transformer vos données brutes en indicateurs utiles : analyses descriptives, prédictives et prescriptives.",
        "icon": "barchart-3",
        "image": "data-bi.webp",
        "is_highlight": False,
        "full_desc": "Vos données regorgent de leviers de croissance inexploités. Nous concevons des tableaux de bord dynamiques et des pipelines d'analyse pour guider vos décisions stratégiques en temps réel.",
        "deliverables": [
            "Collecte, nettoyage et structuration des sources de données disparates",
            "Conception d'entrepôts de données (Data Warehouse) performants",
            "Création de tableaux de bord de pilotage interactifs (Power BI, solutions sur mesure)",
            "Formation de vos cadres à la lecture et au pilotage par la donnée",
        ],
    },
    {
        "id": "web_mobile",
        "slug": "applications-web-mobile",
        "title": "Applications Web & Mobile",
        "short_desc": "Développement d'applications métier sur mesure, plateformes de gestion et API, du cahier des charges à la mise en production.",
        "icon": "code-2",
        "image": "web-mobile.webp",
        "is_highlight": False,
        "full_desc": "Quand les logiciels standards ne répondent pas à vos processus uniques, nous concevons des applications web et mobiles robustes, ergonomiques et pérennes adaptées à votre réalité opérationnelle.",
        "deliverables": [
            "Cadrage fonctionnel, prototypage d'interface (UI/UX) et spécifications",
            "Développement backend & frontend sécurisé (Django, React, Flutter)",
            "Interconnexion d'API et intégration aux logiciels d'entreprise existants",
            "Garantie, maintenance évolutive et accompagnement au déploiement",
        ],
    },
    {
        "id": "agence_digitale",
        "slug": "agence-web-digitale",
        "title": "Agence Web & Digitale",
        "short_desc": "Sites vitrines et e-commerce, identité numérique et présence en ligne qui valorisent votre marque.",
        "icon": "globe",
        "image": "agence-digitale.webp",
        "is_highlight": False,
        "full_desc": "Votre vitrine digitale est votre premier commercial. Nous créons des sites web professionnels, rapides, optimisés pour le référencement naturel (SEO) et conçus pour générer des prospects qualifiés.",
        "deliverables": [
            "Création et refonte de sites web d'entreprise institutionnels et vitrines",
            "Plateformes e-commerce sécurisées avec intégration des paiements locaux",
            "Optimisation du référencement naturel (SEO) pour le marché ivoirien et régional",
            "Conception d'identités visuelles numériques (chartes, logos, supports digitaux)",
        ],
    },
    {
        "id": "sur_mesure",
        "slug": "solutions-sur-mesure",
        "title": "Solutions sur mesure",
        "short_desc": "Fourniture et intégration de matériels et logiciels adaptés à vos contraintes techniques et budgétaires.",
        "icon": "cpu",
        "image": "sur-mesure.webp",
        "is_highlight": False,
        "full_desc": "Chaque organisation fait face à des défis spécifiques. Nous sélectionnons, fournissons et intégrons les technologies exactes dont vous avez besoin, au juste coût et sans superflu.",
        "deliverables": [
            "Conseil indépendant sur le choix des progiciels et matériels",
            "Intégration d'ERP, CRM et outils de facturation/gestion d'activité",
            "Mise en place de solutions sur mesure pour le secteur industriel et tertiaire",
            "Contrat de support sur mesure avec interlocuteur dédié",
        ],
    },
]

VALUES_LIST = [
    {
        "number": "01",
        "title": "Innovation",
        "icon": "lightbulb",
        "description": "Créer et améliorer en permanence pour répondre aux besoins et défis actuels de vos métiers.",
    },
    {
        "number": "02",
        "title": "Qualité",
        "icon": "award",
        "description": "Respecter les standards d'excellence les plus stricts et dépasser systématiquement les attentes de nos clients.",
    },
    {
        "number": "03",
        "title": "Responsabilité",
        "icon": "shield",
        "description": "Assumer pleinement nos engagements envers nos clients, nos équipes, nos partenaires et notre environnement.",
    },
    {
        "number": "04",
        "title": "Collaboration",
        "icon": "handshake",
        "description": "Travailler main dans la main avec vos équipes et partager nos compétences pour bâtir un succès durable.",
    },
]

METHOD_STEPS = [
    {
        "step": "1",
        "title": "Écoute & diagnostic",
        "description": "Nous analysons votre contexte, vos enjeux métier, vos contraintes et l'état de votre existant.",
    },
    {
        "step": "2",
        "title": "Conception",
        "description": "Nous élaborons une solution sur mesure, chiffrée, réaliste et adaptée à votre budget.",
    },
    {
        "step": "3",
        "title": "Déploiement",
        "description": "Nous mettons en œuvre les architectures, testons rigoureusement et formons vos équipes.",
    },
    {
        "step": "4",
        "title": "Support & évolution",
        "description": "Nous assurons la maintenance continue, le suivi opérationnel et faisons évoluer la solution.",
    },
]

CLIENT_REFERENCES = [
    {"name": "Quartz SA", "logo": "quartz.png"},
    {"name": "Altior Partners", "logo": "altior-partners.png"},
    {"name": "Recyplast", "logo": "recyplast.png"},
    {"name": "PITO", "logo": "pito.png"},
    {"name": "Ryg Möbel", "logo": "ryg-mobel.png"},
    {"name": "Agile Construction", "logo": "agile-construction.png"},
    {"name": "JAAS", "logo": "jaas.png"},
]

EXPERTISE_POLES = [
    {
        "id": "direction",
        "title": "Direction & Gouvernance IT",
        "desc": "Cadrage stratégique, audit des systèmes d'information, urbanisation et alignement IT sur vos objectifs d'affaires.",
        "icon": "compass",
        "tag": "Pilotage & Stratégie",
    },
    {
        "id": "infrastructure",
        "title": "Infrastructures, Cloud & Systèmes",
        "desc": "Architecture réseau Cisco, administration de serveurs hybrides, virtualisation VMware/Hyper-V et infogérance.",
        "icon": "server",
        "tag": "Haute Disponibilité",
    },
    {
        "id": "cybersecurite",
        "title": "Cybersécurité & Continuité",
        "desc": "Défense périmétrique, plans de reprise d'activité (PRA/PCA), politique de sauvegarde immuable et conformité.",
        "icon": "shield-check",
        "tag": "Protection Active",
    },
    {
        "id": "data_apps",
        "title": "Data, BI & Applications",
        "desc": "Conception d'applications métier sur mesure (Web & Mobile), tableaux de bord décisionnels Power BI et intégration ERP.",
        "icon": "code-2",
        "tag": "Agilité & Décisionnel",
    },
]

KEY_METRICS = [
    {
        "value": "+10 ans",
        "num_target": "10",
        "prefix": "+",
        "suffix": " ans",
        "label": "Années d'expérience IT",
        "description": "Cabinet fondé et ancré à Abidjan",
        "icon": "clock",
    },
    {
        "value": "+50",
        "num_target": "50",
        "prefix": "+",
        "suffix": "",
        "label": "Projets & Déploiements",
        "description": "Infrastructures et logiciels livrés",
        "icon": "layers",
    },
    {
        "value": "+30",
        "num_target": "30",
        "prefix": "+",
        "suffix": "",
        "label": "Entreprises clientes",
        "description": "PME et organisations accompagnées",
        "icon": "shield-check",
    },
    {
        "value": "99.8%",
        "num_target": "99.8",
        "prefix": "",
        "suffix": "%",
        "label": "Disponibilité garantie",
        "description": "Continuité d'activité et support SLA",
        "icon": "zap",
    },
]


class HomeView(View):
    """Page d'accueil principale"""

    def get(self, request):
        form = ContactForm()
        context = {
            "services": SERVICES_CATALOG,
            "values": VALUES_LIST,
            "steps": METHOD_STEPS,
            "references": CLIENT_REFERENCES,
            "metrics": KEY_METRICS,
            "form": form,
            "is_home": True,
        }
        return render(request, "showcase/home.html", context)

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_msg = form.save(commit=False)
            # Capture de l'IP du client de manière sécurisée
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                contact_msg.ip_address = x_forwarded_for.split(",")[0].strip()
            else:
                contact_msg.ip_address = request.META.get("REMOTE_ADDR")
            contact_msg.save()

            # Envoi d'e-mail optionnel (sans bloquer si le serveur mail échoue)
            try:
                subject = f"[Hadena Site] Nouveau contact de {contact_msg.full_name} ({contact_msg.get_service_display()})"
                body = (
                    f"Nouveau message reçu depuis le site web Hadena Limited :\n\n"
                    f"Nom : {contact_msg.full_name}\n"
                    f"Entreprise : {contact_msg.company or 'N/A'}\n"
                    f"Email : {contact_msg.email}\n"
                    f"Téléphone : {contact_msg.phone}\n"
                    f"Service : {contact_msg.get_service_display()}\n\n"
                    f"Message :\n{contact_msg.message}\n"
                )
                send_mail(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.CONTACT_RECIPIENT],
                    fail_silently=True,
                )
            except Exception as e:
                logger.warning("Échec de l'envoi de l'e-mail de notification: %s", e)

            messages.success(
                request,
                "Merci pour votre message ! Notre équipe technique vous recontactera dans les meilleurs délais (sous 48h ouvrées).",
            )
            return redirect("showcase:home")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous avant d'envoyer votre demande.")
            context = {
                "services": SERVICES_CATALOG,
                "values": VALUES_LIST,
                "steps": METHOD_STEPS,
                "references": CLIENT_REFERENCES,
                "metrics": KEY_METRICS,
                "form": form,
                "is_home": True,
            }
            return render(request, "showcase/home.html", context)


class AboutView(View):
    """Page Qui sommes-nous & Mot de la gérante."""

    def get(self, request):
        context = {
            "values": VALUES_LIST,
            "references": CLIENT_REFERENCES,
            "metrics": KEY_METRICS,
            "expertise_poles": EXPERTISE_POLES,
            "page_title": "Qui sommes-nous | Hadena Limited",
            "meta_description": "Découvrez Hadena Limited, ses valeurs, ses pôles d'experts IT et le mot de la gérante basée à Abidjan.",
        }
        return render(request, "showcase/about.html", context)


class ServicesView(View):
    """Page catalogue complet des services IT."""

    def get(self, request):
        context = {
            "services": SERVICES_CATALOG,
            "page_title": "Services IT & Expertises | Hadena Limited",
            "meta_description": "Découvrez nos 9 expertises IT : gouvernance, réseaux, cybersécurité, audit, maintenance, BI et applications web/mobile.",
        }
        return render(request, "showcase/services.html", context)


class ServiceDetailView(View):
    """Vue détaillée pour une expertise spécifique."""

    def get(self, request, slug):
        service = next((s for s in SERVICES_CATALOG if s["slug"] == slug), None)
        if not service:
            return redirect("showcase:services")
        form = ContactForm(initial={"service": service["id"]})
        context = {
            "service": service,
            "all_services": SERVICES_CATALOG,
            "form": form,
            "page_title": f"{service['title']} | Hadena Limited",
            "meta_description": service["short_desc"],
        }
        return render(request, "showcase/service_detail.html", context)


class ProductsView(View):
    """Page Produits : Matériels et Logiciels professionnels."""

    def get(self, request):
        form = ContactForm(initial={"service": "produits"})
        context = {
            "form": form,
            "page_title": "Matériels & Logiciels informatiques | Hadena Limited",
            "meta_description": "Fourniture, conseil et installation d'ordinateurs, serveurs, routeurs, licences cloud et progiciels à Abidjan.",
        }
        return render(request, "showcase/products.html", context)


class TrainingView(View):
    """Page Formations professionnelles."""

    def get(self, request):
        form = ContactForm(initial={"service": "formation"})
        context = {
            "form": form,
            "page_title": "Formations informatiques professionnelles | Hadena Limited",
            "meta_description": "Montez en compétences avec nos formations pratiques en bureautique, sécurité, data et administration système à Abidjan.",
        }
        return render(request, "showcase/training.html", context)


class ContactView(View):
    """Page dédiée Contact & Demande de devis."""

    def get(self, request):
        form = ContactForm()
        return render(request, "showcase/contact.html", {"form": form})

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_msg = form.save(commit=False)
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                contact_msg.ip_address = x_forwarded_for.split(",")[0].strip()
            else:
                contact_msg.ip_address = request.META.get("REMOTE_ADDR")
            contact_msg.save()

            # Envoi d'e-mail de notification
            try:
                subject = f"[Hadena Site] Nouveau contact de {contact_msg.full_name} ({contact_msg.get_service_display()})"
                body = (
                    f"Nouveau message reçu depuis le site web Hadena Limited :\n\n"
                    f"Nom : {contact_msg.full_name}\n"
                    f"Entreprise : {contact_msg.company or 'N/A'}\n"
                    f"Email : {contact_msg.email}\n"
                    f"Téléphone : {contact_msg.phone}\n"
                    f"Service : {contact_msg.get_service_display()}\n\n"
                    f"Message :\n{contact_msg.message}\n"
                )
                send_mail(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.CONTACT_RECIPIENT],
                    fail_silently=True,
                )
            except Exception as e:
                logger.warning("Échec de l'envoi de l'e-mail de notification: %s", e)

            messages.success(
                request,
                "Votre demande a bien été envoyée ! Un conseiller d'Hadena Limited vous répondra sous 48h ouvrées.",
            )
            return redirect("showcase:contact")
        else:
            messages.error(request, "Veuillez vérifier les champs du formulaire.")
            return render(request, "showcase/contact.html", {"form": form})


@method_decorator(csrf_exempt, name="dispatch")
class SetCookieConsentView(View):
    """Enregistre le choix du visiteur sur les cookies (RGPD). Supporte GET, POST et AJAX."""

    def _handle_consent(self, request, consent_choice):
        choice = "rejected" if consent_choice == "rejected" else "accepted"
        is_ajax = (
            request.headers.get("x-requested-with") == "XMLHttpRequest"
            or "application/json" in request.headers.get("accept", "")
        )

        if is_ajax:
            response = JsonResponse({"status": "ok", "consent": choice})
        else:
            redirect_url = request.META.get("HTTP_REFERER") or "/"
            response = HttpResponseRedirect(redirect_url)

        # Cookie persistant 1 an, SameSite Lax, HttpOnly False pour interopérabilité JS
        response.set_cookie(
            "hadena_cookie_consent",
            choice,
            max_age=365 * 24 * 3600,
            samesite="Lax",
            secure=False,
        )
        return response

    def get(self, request):
        consent_choice = request.GET.get("consent", "accepted")
        return self._handle_consent(request, consent_choice)

    def post(self, request):
        consent_choice = request.POST.get("consent") or request.GET.get("consent", "accepted")
        return self._handle_consent(request, consent_choice)


class MentionsLegalesView(View):
    """Mentions légales obligatoires."""

    def get(self, request):
        return render(request, "legal/mentions_legales.html")


class PrivacyPolicyView(View):
    """Politique de confidentialité et protection des données (RGPD)."""

    def get(self, request):
        return render(request, "legal/privacy.html")
