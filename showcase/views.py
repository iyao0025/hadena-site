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
        "family": "conseil_audit",
        "family_label": "Conseil & Audit",
        "action_label": "Découvrir la gouvernance IT",
        "image": "gouvernance.webp",
        "is_highlight": True,
        "tech_badges": ["ITIL v4", "AMOA", "Schéma directeur", "Audit SI"],
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
        "family": "infrastructure_securite",
        "family_label": "Infrastructures & Sécurité",
        "action_label": "Explorer les systèmes & réseaux",
        "image": "reseaux.webp",
        "is_highlight": False,
        "tech_badges": ["Cisco", "Windows Server", "Linux", "VMware", "Cloud"],
        "full_desc": "Une infrastructure réseau performante et résiliente est l'épine dorsale de votre entreprise. Hadena Limited conçoit, déploie et supervise vos architectures locales, hybrides ou cloud pour garantir une disponibilité maximale.",
        "deliverables": [
            "Architecture et câblage réseau haute disponibilité (LAN, WAN, Wi-Fi pro)",
            "Virtualisation et administration des serveurs (Windows Server, Linux)",
            "Migration et hébergement cloud (IaaS, PaaS, solutions de messagerie)",
            "Supervision continue et astreinte 24/7 sous contrat cadre",
        ],
    },
    {
        "id": "securite",
        "slug": "securite-informatique",
        "title": "Sécurité informatique",
        "short_desc": "Analyse des risques, durcissement des systèmes, sauvegardes et plans de continuité pour protéger vos données.",
        "icon": "shield-check",
        "family": "infrastructure_securite",
        "family_label": "Infrastructures & Sécurité",
        "action_label": "Explorer la sécurité informatique",
        "image": "securite.webp",
        "is_highlight": False,
        "tech_badges": ["Firewall Fortinet", "EDR Managé", "Sauvegarde 3-2-1", "PRA / PCA"],
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
        "family": "conseil_audit",
        "family_label": "Conseil & Audit",
        "action_label": "Découvrir l'audit informatique",
        "image": "audit.webp",
        "is_highlight": False,
        "tech_badges": ["Tests d'intrusion", "Audit conformité", "Inventaire parc", "Plan remédiation"],
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
        "family": "infrastructure_securite",
        "family_label": "Infrastructures & Sécurité",
        "action_label": "Découvrir le Service Desk",
        "image": "maintenance.webp",
        "is_highlight": False,
        "tech_badges": ["Support N1/N2/N3", "Téléassistance", "SLA Garanti", "Ticketing"],
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
        "family": "data_dev",
        "family_label": "Data & Développement",
        "action_label": "Explorer la Data Analytics & BI",
        "image": "data-bi.webp",
        "is_highlight": False,
        "tech_badges": ["Power BI", "SQL Server", "Data Warehouse", "ETL Pipelines"],
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
        "family": "data_dev",
        "family_label": "Data & Développement",
        "action_label": "Découvrir le développement sur mesure",
        "image": "web-mobile.webp",
        "is_highlight": False,
        "tech_badges": ["Django / Python", "React", "Flutter", "PostgreSQL", "API REST"],
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
        "family": "data_dev",
        "family_label": "Data & Développement",
        "action_label": "Explorer l'Agence Web & Digitale",
        "image": "agence-digitale.webp",
        "is_highlight": False,
        "tech_badges": ["Sites Corporate", "E-Commerce", "SEO Local", "Identité Visuelle"],
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
        "family": "solutions_sur_mesure",
        "family_label": "Solutions d'Entreprise",
        "action_label": "Découvrir les solutions sur mesure",
        "image": "sur-mesure.webp",
        "is_highlight": False,
        "tech_badges": ["Intégration ERP", "CRM", "Matériels pros", "Contrats support"],
        "full_desc": "Chaque organisation fait face à des défis spécifiques. Nous sélectionnons, fournissons et intégrons les technologies exactes dont vous avez besoin, au juste coût et sans superflu.",
        "deliverables": [
            "Conseil indépendant sur le choix des progiciels et matériels",
            "Intégration d'ERP, CRM et outils de facturation/gestion d'activité",
            "Mise en place de solutions sur mesure pour le secteur industriel et tertiaire",
            "Contrat de support sur mesure avec interlocuteur dédié",
        ],
    },
]

SERVICE_FAMILIES = [
    {"id": "all", "label": "Toutes les expertises", "count": 9},
    {"id": "conseil_audit", "label": "Conseil & Audit", "count": 2},
    {"id": "infrastructure_securite", "label": "Infrastructures & Sécurité", "count": 3},
    {"id": "data_dev", "label": "Data & Développement", "count": 3},
    {"id": "solutions_sur_mesure", "label": "Solutions d'Entreprise", "count": 1},
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
        initial_data = {}
        if "service" in request.GET:
            initial_data["service"] = request.GET.get("service")
        form = ContactForm(initial=initial_data)
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
            "service_families": SERVICE_FAMILIES,
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


HARDWARE_PRODUCTS = [
    {
        "id": "ordinateurs_stations",
        "title": "Ordinateurs & Stations de travail",
        "desc": "Portables d'entreprise ultra-légers, unités centrales sécurisées et stations graphiques fixes taillées pour la productivité intensive.",
        "icon": "monitor",
        "brands": ["HP ProBook/Elite", "Dell Latitude/OptiPlex", "Lenovo ThinkPad"],
        "badge": "Postes Professionnels",
        "warranty": "Garantie constructeur 1 à 3 ans",
    },
    {
        "id": "serveurs_stockage",
        "title": "Serveurs & Baies de stockage",
        "desc": "Serveurs d'entreprise rack ou tour, baies SAN/NAS haute capacité, disques d'entreprise et onduleurs de protection électrique.",
        "icon": "server",
        "brands": ["Dell PowerEdge", "HPE ProLiant", "Synology NAS", "APC / Eaton"],
        "badge": "Datacenter & Salle Serveurs",
        "warranty": "Configuration RAID & support sur site",
    },
    {
        "id": "reseaux_wifi",
        "title": "Équipements Réseau & Wi-Fi",
        "desc": "Switches manageables Gigabit/10G, routeurs d'entreprise, bornes Wi-Fi 6 haute densité et passerelles firewall nouvelle génération.",
        "icon": "wifi",
        "brands": ["Cisco Catalyst", "Fortinet FortiGate", "Ubiquiti UniFi", "MikroTik"],
        "badge": "Haute Disponibilité",
        "warranty": "Paramétrage VLAN & QoS inclus",
    },
    {
        "id": "peripheriques_imagerie",
        "title": "Périphériques & Imagerie",
        "desc": "Imprimantes réseau multifonctions laser, scanners de numérisation grand volume, écrans ergonomiques et accessoires pros.",
        "icon": "printer",
        "brands": ["HP LaserJet", "Canon", "Epson WorkForce", "Dell Displays"],
        "badge": "Bureautique d'Entreprise",
        "warranty": "Installation réseau prête à l'emploi",
    },
]

SOFTWARE_PRODUCTS = [
    {
        "id": "bureautique_os",
        "title": "Suites Bureautiques & Systèmes OS",
        "desc": "Licences Microsoft 365 Entreprise, Windows 11 Professionnel, messagerie Exchange managée et outils collaboratifs sécurisés.",
        "icon": "app-window",
        "brands": ["Microsoft 365", "Windows 11 Pro", "Exchange Online", "Teams"],
        "badge": "Productivité & Collaboration",
        "warranty": "Licences conformes & activation officielle",
    },
    {
        "id": "securite_sauvegarde",
        "title": "Sécurité, Antivirus & Sauvegarde",
        "desc": "Solutions antivirus managées, EDR contre les ransomwares, sauvegardes immuables locales/cloud et certificats de conformité.",
        "icon": "shield-check",
        "brands": ["Kaspersky Endpoint", "Fortinet EDR", "Veeam Backup", "Acronis Cyber"],
        "badge": "Cybersécurité Active",
        "warranty": "Déploiement centralisé & console d'administration",
    },
    {
        "id": "progiciels_erp_crm",
        "title": "Progiciels de Gestion (ERP & CRM)",
        "desc": "Logiciels de comptabilité, gestion commerciale, paie RH et solutions ERP/CRM intégrées à vos processus métiers en Côte d'Ivoire.",
        "icon": "layers",
        "brands": ["Sage 100", "Odoo ERP", "Solutions CRM sur mesure", "Paie & RH"],
        "badge": "Pilotage Métier",
        "warranty": "Migration de données & formation utilisateurs",
    },
    {
        "id": "cloud_saas",
        "title": "Infrastructures Cloud & Solutions SaaS",
        "desc": "Abonnements cloud d'entreprise, serveurs virtuels VPS/IaaS, sauvegardes externalisées haute résilience et certificats SSL.",
        "icon": "cloud",
        "brands": ["Microsoft Azure", "Amazon Web Services (AWS)", "Google Cloud", "Hébergement dédié"],
        "badge": "Évolutivité Cloud",
        "warranty": "Monitoring 24/7 & optimisation des coûts",
    },
]

EQUIPMENT_FAQS = [
    {
        "question": "Quels sont les délais de livraison pour les matériels informatiques à Abidjan ?",
        "answer": "Pour les équipements en stock (ordinateurs portables, postes de travail, switches standards, périphériques), la livraison intervient sous 24 à 48 heures ouvrées sur toute la région d'Abidjan. Pour les serveurs configurés sur mesure ou les baies spécifiques, le délai moyen est communiqué dès l'émission de la facture proforma.",
    },
    {
        "question": "Délivrez-vous des factures proforma pour validation budgétaire ?",
        "answer": "Absolument. Nous émettons des factures proforma complètes, détaillées et chiffrées sous 48 heures ouvrées maximum, conformes aux exigences administratives et comptables des entreprises et institutions en Côte d'Ivoire.",
    },
    {
        "question": "L'installation et la configuration sur site sont-elles incluses ?",
        "answer": "Oui, selon vos besoins. Nos ingénieurs peuvent livrer vos équipements prêts à l'emploi (mastering des postes, jonction au domaine Active Directory, paramétrage des réseaux et des droits d'accès) et assurer l'installation physique dans vos locaux à Abidjan.",
    },
    {
        "question": "Comment fonctionnent la garantie constructeur et le service après-vente (SAV) ?",
        "answer": "Tous nos équipements bénéficient de la garantie constructeur officielle (1 à 3 ans selon les gammes avec pièces et main-d'œuvre). En cas d'incident, Hadena Limited assure le diagnostic, le relais technique et la prise en charge SAV pour minimiser toute interruption d'activité.",
    },
]


class ProductsView(View):
    """Page Produits : Matériels et Logiciels professionnels."""

    def get(self, request):
        form = ContactForm(initial={"service": "sur_mesure"})
        context = {
            "hardware_products": HARDWARE_PRODUCTS,
            "software_products": SOFTWARE_PRODUCTS,
            "equipment_faqs": EQUIPMENT_FAQS,
            "references": CLIENT_REFERENCES,
            "form": form,
            "page_title": "Matériels & Logiciels informatiques | Hadena Limited",
            "meta_description": "Fourniture, conseil et installation d'ordinateurs, serveurs, routeurs, licences cloud et progiciels à Abidjan.",
        }
        return render(request, "showcase/products.html", context)


TRAINING_MODULES = [
    {
        "id": "bureautique_collaboratif",
        "title": "Bureautique & Outils Collaboratifs",
        "short_desc": "Maîtrise avancée d'Excel, Word, PowerPoint et adoption fluide des outils cloud (Microsoft 365, Teams, OneDrive).",
        "icon": "file-spreadsheet",
        "badge_color": "emerald",
        "profile": "collaborateurs",
        "profile_label": "Collaborateurs",
        "duration": "2 à 3 jours (14h à 21h)",
        "duration_badge": "2 à 3 jours",
        "level": "Tous niveaux",
        "level_bars": 1,
        "target_audience": "Assistants, cadres, équipes administratives & opérationnelles",
        "format": "Intra ou Inter-entreprises",
        "price_hint": "À partir de 150 000 FCFA / participant",
        "objectives": [
            "Automatiser les calculs complexes et tableaux de bord avec Excel (fonctions avancées, TCD)",
            "Collaborer efficacement en temps réel sur Microsoft Teams et SharePoint",
            "Gagner un temps précieux dans la rédaction et la mise en forme de documents d'entreprise",
        ],
        "prerequisites": "Utilisation courante d'un ordinateur sous Windows ou macOS.",
        "course_outline": [
            "Module 1 : Formules avancées, RechercheX, Si imbriqués et validation de données",
            "Module 2 : Tableaux croisés dynamiques et mise en forme conditionnelle visuelle",
            "Module 3 : Co-édition en direct sur OneDrive et gestion d'équipes sur Teams",
            "Module 4 : Astuces de productivité et raccourcis professionnels indispensables",
        ],
        "cert_deliverable": "Attestation nominative Hadena Limited + Évaluation pratique des acquis",
    },
    {
        "id": "cybersecurite_sensibilisation",
        "title": "Cybersécurité & Bonnes Pratiques",
        "short_desc": "Sensibilisation aux cybermenaces, réflexes face au phishing, gestion sécurisée des accès et protection des données sensibles.",
        "icon": "shield-check",
        "badge_color": "rose",
        "profile": "collaborateurs",
        "profile_label": "Collaborateurs",
        "duration": "1 jour (7h)",
        "duration_badge": "1 jour",
        "level": "Sensibilisation",
        "level_bars": 1,
        "target_audience": "Ensemble des collaborateurs manipulant des postes et données d'entreprise",
        "format": "Intra-entreprise sur site ou visio",
        "price_hint": "Formule session groupe dès 350 000 FCFA",
        "objectives": [
            "Identifier immédiatement les courriels de phishing, spear-phishing et faux ordres de virement",
            "Adopter les réflexes d'hygiène numérique (mots de passe robustes, MFA, verrouillage de session)",
            "Savoir comment réagir et alerter en cas de comportement suspect ou d'incident de sécurité",
        ],
        "prerequisites": "Aucun prérequis technique.",
        "course_outline": [
            "Module 1 : Panorama des cybermenaces actuelles en Côte d'Ivoire et Afrique de l'Ouest",
            "Module 2 : Anatomie d'une attaque par phishing et ateliers d'analyse de faux e-mails",
            "Module 3 : Sécurité des mots de passe, coffres-forts numériques et double facteur (MFA)",
            "Module 4 : Sécurité en déplacement, Wi-Fi publics, clés USB et procédure d'alerte interne",
        ],
        "cert_deliverable": "Attestation d'habilitation à l'hygiène numérique Hadena Limited",
    },
    {
        "id": "data_power_bi",
        "title": "Analyse de Données & Power BI",
        "short_desc": "Collecte, modélisation de données (Power Query, DAX) et conception de tableaux de bord décisionnels interactifs percutants.",
        "icon": "bar-chart-3",
        "badge_color": "amber",
        "profile": "collaborateurs",
        "profile_label": "Collaborateurs & Décideurs",
        "duration": "3 à 5 jours (21h à 35h)",
        "duration_badge": "3 à 5 jours",
        "level": "Intermédiaire à Avancé",
        "level_bars": 2,
        "target_audience": "Contrôleurs de gestion, analystes financiers, marketeurs, managers de pôle",
        "format": "Intra ou Inter-entreprises",
        "price_hint": "À partir de 275 000 FCFA / participant",
        "objectives": [
            "Importer et transformer des données de sources multiples avec Power Query",
            "Maîtriser les formules DAX fondamentales (CALCULATE, RELATED, ratios temporels)",
            "Créer des rapports interactifs dynamiques prêts pour le comité de direction",
        ],
        "prerequisites": "Bonne pratique préalable d'Excel (formules et Tableaux Croisés Dynamiques).",
        "course_outline": [
            "Module 1 : Découverte de l'écosystème Power BI Desktop et cycle décisionnel",
            "Module 2 : Importation, nettoyage et modélisation en étoile dans Power Query",
            "Module 3 : Les bases et subtilités du langage DAX pour les métriques clés",
            "Module 4 : Data Visualisation : graphiques percutants, filtres croisés et publication sur le service cloud",
        ],
        "cert_deliverable": "Attestation Hadena Data Analytics + Préparation à l'examen Microsoft PL-300",
    },
    {
        "id": "admin_systemes_reseaux",
        "title": "Administration Systèmes & Réseaux",
        "short_desc": "Déploiement et administration de Windows Server, Linux, virtualisation (VMware/Hyper-V) et équipements Cisco/Fortinet.",
        "icon": "server",
        "badge_color": "sky",
        "profile": "techniciens",
        "profile_label": "Techniciens & Admins",
        "duration": "5 jours (35h)",
        "duration_badge": "5 jours",
        "level": "Avancé / Technique",
        "level_bars": 3,
        "target_audience": "Administrateurs réseaux, techniciens de maintenance, ingénieurs système",
        "format": "Intra ou Inter-entreprises en lab dédié",
        "price_hint": "À partir de 450 000 FCFA / participant",
        "objectives": [
            "Installer, configurer et sécuriser un contrôleur de domaine Active Directory et DNS/DHCP",
            "Administrer des machines virtuelles et gérer le stockage haute disponibilité",
            "Configurer des commutateurs VLAN, routage sécurisé et règles pare-feu de périmètre",
        ],
        "prerequisites": "Connaissances solides en informatique générale et notions de réseaux TCP/IP.",
        "course_outline": [
            "Module 1 : Déploiement Windows Server, rôles AD DS, GPO et gestion des habilitations",
            "Module 2 : Fondamentaux Linux d'entreprise (gestion des services, droits, scripts shell)",
            "Module 3 : Virtualisation d'infrastructure, hyperviseurs et stratégies de sauvegarde PRA",
            "Module 4 : Configuration switches manageables, VLANs, Wi-Fi d'entreprise et pare-feu",
        ],
        "cert_deliverable": "Attestation d'expertise technique Hadena + Préparation CCNA / Microsoft AZ-800",
    },
    {
        "id": "itil_gouvernance",
        "title": "Gestion des Services IT (ITIL v4)",
        "short_desc": "Structuration du Service Desk, gestion des incidents, problèmes et changements selon les standards internationaux ITIL v4.",
        "icon": "workflow",
        "badge_color": "indigo",
        "profile": "managers",
        "profile_label": "Managers & DSI",
        "duration": "3 jours (21h)",
        "duration_badge": "3 jours",
        "level": "Intermédiaire / Cadre",
        "level_bars": 2,
        "target_audience": "DSI, Responsables informatiques, chefs de projets, superviseurs Helpdesk",
        "format": "Intra ou Inter-entreprises",
        "price_hint": "À partir de 350 000 FCFA / participant",
        "objectives": [
            "Comprendre et appliquer le Système de Valeur des Services (SVS) ITIL v4",
            "Mettre en place un guichet unique (Service Desk) avec SLA garantis",
            "Améliorer continuellement la satisfaction des directions métiers et des utilisateurs finaux",
        ],
        "prerequisites": "Expérience préalable en environnement informatique ou gestion de projet.",
        "course_outline": [
            "Module 1 : Les 4 dimensions et les 7 principes directeurs d'ITIL v4",
            "Module 2 : Pratiques de gestion de services : Gestion des Incidents, Problèmes et Demandes",
            "Module 3 : Pratiques de gestion générale : Amélioration continue et gestion des changements",
            "Module 4 : Cas pratiques de modélisation de catalogue de services et préparation examen",
        ],
        "cert_deliverable": "Attestation Hadena Gouvernance IT + Préparation officielle certification ITIL v4 Foundation",
    },
    {
        "id": "programme_sur_mesure",
        "title": "Ingénierie de Formation sur Mesure",
        "short_desc": "Conception de programmes personnalisés calqués sur vos logiciels métiers, vos processus internes et vos contraintes d'agenda.",
        "icon": "sparkles",
        "badge_color": "purple",
        "profile": "managers",
        "profile_label": "Directions & DRH",
        "duration": "Flexible selon vos besoins",
        "duration_badge": "Sur mesure",
        "level": "Personnalisé",
        "level_bars": 2,
        "target_audience": "Directions générales, DRH, DSI souhaitant former des équipes complètes",
        "format": "Sur site client ou en séminaire dédié",
        "price_hint": "Proposition budgétaire détaillée sous 48h",
        "objectives": [
            "Adapter 100% des contenus aux cas d'usage réels et données fictives de votre secteur",
            "Former vos collaborateurs directement sur vos outils propriétaires (ERP, CRM, portails)",
            "Planifier des sessions en demi-journées ou week-ends pour préserver la continuité d'activité",
        ],
        "prerequisites": "Définis conjointement lors de l'entretien de cadrage pédagogique.",
        "course_outline": [
            "Étape 1 : Diagnostic des compétences initiales et identification des écarts opérationnels",
            "Étape 2 : Co-conception des supports de cours personnalisés et des ateliers pratiques",
            "Étape 3 : Animation dynamique par un consultant-formateur expert du domaine",
            "Étape 4 : Évaluation post-formation et rapport d'impact remis à la direction",
        ],
        "cert_deliverable": "Attestation nominative d'entreprise personnalisée avec livret de synthèse",
    },
]

TRAINING_PROFILES = [
    {"id": "all", "label": "Tous les profils", "count": 6},
    {"id": "collaborateurs", "label": "Collaborateurs & Utilisateurs", "count": 3},
    {"id": "techniciens", "label": "Techniciens & Admins", "count": 1},
    {"id": "managers", "label": "Managers & Décideurs", "count": 2},
]

TRAINING_FORMATS = [
    {
        "id": "intra",
        "title": "Formation Intra-entreprise",
        "badge": "Dans vos locaux ou sur site",
        "icon": "building-2",
        "desc": "Sessions privatisées exclusivement dédiées à vos équipes, organisées dans vos locaux à Abidjan ou partout en Côte d'Ivoire, avec adaptation des exemples à votre contexte d'affaires.",
        "advantages": [
            "Programme ajusté à vos outils et problématiques métiers",
            "Dates et horaires fixés selon vos impératifs d'agenda",
            "Tarif dégressif avantageux pour les groupes de 4 à 15 collaborateurs",
            "Exercices pratiques directement sur vos équipements d'entreprise",
        ],
    },
    {
        "id": "inter",
        "title": "Formation Inter-entreprises",
        "badge": "Sessions collectives en centre",
        "icon": "users",
        "desc": "Sessions collectives en petits groupes (4 à 8 participants max) regroupant des professionnels issus de différentes entreprises dans des salles équipées modernes et climatisées à Abidjan.",
        "advantages": [
            "Idéal pour former 1 ou 2 collaborateurs sans mobiliser tout un service",
            "Partage d'expériences enrichissant avec des pairs d'autres secteurs",
            "Émulation de groupe et lab informatique individuel haute performance",
            "Calendrier de dates régulières tout au long de l'année",
        ],
    },
    {
        "id": "accompagnement",
        "title": "Accompagnement Post-formation",
        "badge": "Ancrage des compétences",
        "icon": "life-buoy",
        "desc": "Parce qu'une formation ne s'arrête pas au dernier jour de cours, nos formateurs restent disponibles pour assister vos apprenants dans la mise en pratique réelle de leurs acquis.",
        "advantages": [
            "Supports de cours complets (PDF, mémentos, fichiers d'exercices corrigés)",
            "Assistance téléassistance / questions-réponses durant 30 jours après la session",
            "Évaluation des acquis à froid après 3 semaines de mise en pratique",
            "Recommandations d'axes de progression remises au responsable formation/RH",
        ],
    },
]

UPCOMING_SESSIONS = [
    {
        "course": "Analyse de Données & Power BI",
        "date": "15 au 18 Décembre 2026",
        "duration": "4 jours (28h)",
        "location": "Abidjan (Cocody)",
        "seats": "3 places disponibles",
        "status": "Inscriptions ouvertes",
    },
    {
        "course": "Cybersécurité & Bonnes Pratiques",
        "date": "08 Janvier 2027",
        "duration": "1 jour (7h)",
        "location": "Abidjan & Format Hybride",
        "seats": "5 places disponibles",
        "status": "Inscriptions ouvertes",
    },
    {
        "course": "Administration Systèmes & Réseaux",
        "date": "19 au 23 Janvier 2027",
        "duration": "5 jours (35h)",
        "location": "Abidjan (Lab Réseau)",
        "seats": "2 places disponibles",
        "status": "Dernières places",
    },
    {
        "course": "Gestion des Services IT (ITIL v4)",
        "date": "02 au 04 Février 2027",
        "duration": "3 jours (21h)",
        "location": "Abidjan (Cocody)",
        "seats": "4 places disponibles",
        "status": "Inscriptions ouvertes",
    },
]

TRAINING_METHODOLOGY = [
    {
        "step": "01",
        "title": "Diagnostic & Cadrage",
        "desc": "Évaluation du niveau initial des participants et définition précise des compétences opérationnelles ciblées.",
    },
    {
        "step": "02",
        "title": "Cas Réels & Ateliers",
        "desc": "80% de pratique, études de cas concrètes et mises en situation inspirées directement de votre secteur.",
    },
    {
        "step": "03",
        "title": "Évaluation & Attestation",
        "desc": "Validation des acquis en fin de session et remise d'une attestation officielle nominative Hadena Limited.",
    },
    {
        "step": "04",
        "title": "Suivi à 30 jours",
        "desc": "Support continu pendant un mois pour répondre aux questions lors de la mise en application sur le terrain.",
    },
]

TRAINING_METRICS = [
    {"target": 350, "prefix": "+", "suffix": "", "label": "Professionnels formés", "sub": "en entreprise à Abidjan"},
    {"target": 98.4, "prefix": "", "suffix": "%", "label": "Taux de satisfaction", "sub": "évaluations à chaud"},
    {"target": 80, "prefix": "", "suffix": "%", "label": "Pratique & Ateliers", "sub": "orientés cas d'usage réels"},
    {"target": 100, "prefix": "", "suffix": "%", "label": "Attestation nominative", "sub": "délivrée à chaque participant"},
]

TRAINING_FAQS = [
    {
        "question": "Les formations délivrent-elles un certificat ou une attestation ?",
        "answer": "Oui. Chaque participant ayant suivi la session avec assiduité et validé les ateliers pratiques reçoit une attestation officielle nominative délivrée par Hadena Limited, détaillant les compétences acquises et le volume horaire. Pour les parcours certifiants (ITIL v4, Power BI, Cisco), nous dispensons les modules de préparation officielle aux examens éditeurs reconnus à l'échelle internationale.",
    },
    {
        "question": "Où se déroulent les formations (sur site ou en centre) ?",
        "answer": "Nous proposons les deux formules selon vos contraintes : en formule Intra-entreprise directement dans vos locaux d'entreprise (à Abidjan ou dans toute la Côte d'Ivoire) avec notre matériel pédagogique mobile, ou en formule Inter-entreprises dans nos salles de séminaires climatisées et équipées à Cocody.",
    },
    {
        "question": "Les formations peuvent-elles être prises en charge par le FDFP ?",
        "answer": "Absolument. Hadena Limited fournit l'ensemble des pièces administratives et contractuelles requises pour la prise en charge FDFP : conventions de formation, plan de cours détaillé, factures proforma certifiées, feuilles d'émargement quotidiennes et bilans pédagogiques.",
    },
    {
        "question": "Quel est le nombre de participants recommandé par session ?",
        "answer": "Afin de garantir un suivi individualisé de haute qualité et une réelle progression de chacun, nos groupes inter-entreprises sont strictement plafonnés à 8 personnes. En formule intra-entreprise, l'effectif idéal se situe entre 4 et 12 collaborateurs par session.",
    },
    {
        "question": "Le matériel informatique et les logiciels sont-ils fournis ?",
        "answer": "Pour les sessions inter-entreprises, chaque participant dispose d'un ordinateur individuel configuré avec l'ensemble des logiciels et licences nécessaires. Pour les sessions intra-entreprise dans vos locaux, nos formateurs apportent les supports, clés d'exercices et peuvent configurer en amont les postes de vos apprenants.",
    },
]


class TrainingView(View):
    """Page Formations professionnelles."""

    def get(self, request):
        form = ContactForm(initial={"service": "formation"})
        context = {
            "training_modules": TRAINING_MODULES,
            "training_profiles": TRAINING_PROFILES,
            "training_formats": TRAINING_FORMATS,
            "upcoming_sessions": UPCOMING_SESSIONS,
            "training_methodology": TRAINING_METHODOLOGY,
            "training_metrics": TRAINING_METRICS,
            "training_faqs": TRAINING_FAQS,
            "references": CLIENT_REFERENCES,
            "form": form,
            "page_title": "Formations informatiques professionnelles | Hadena Limited",
            "meta_description": "Montez en compétences avec nos formations pratiques en bureautique, sécurité, data et administration système à Abidjan.",
        }
        return render(request, "showcase/training.html", context)


class ContactView(View):
    """Page dédiée Contact & Demande de devis."""

    def get(self, request):
        initial_data = {}
        if "service" in request.GET:
            initial_data["service"] = request.GET.get("service")
        form = ContactForm(initial=initial_data)
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
