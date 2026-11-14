import re

from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """Formulaire de contact et demande de devis avec Honeypot et conformité RGPD."""

    # Champ honeypot invisible : les robots le remplissent, les humains ne le voient pas
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "style": "display:none !important; position:absolute !important; left:-9999px !important;",
            "tabindex": "-1",
            "autocomplete": "off",
        }),
        label="Ne pas remplir",
    )

    consent_gdpr = forms.BooleanField(
        required=True,
        error_messages={
            "required": "Vous devez accepter le traitement de vos données conformément à notre politique de confidentialité pour envoyer ce message."
        },
        label="J'accepte que Hadena Limited traite mes données personnelles pour répondre à ma demande.",
        widget=forms.CheckboxInput(attrs={"class": "checkbox checkbox-primary checkbox-sm"}),
    )

    class Meta:
        model = ContactMessage
        fields = ["full_name", "company", "email", "phone", "service", "message", "consent_gdpr"]
        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "input input-bordered w-full bg-base-100 text-base-content focus:input-primary transition-all duration-200",
                "placeholder": "Votre nom et prénom *",
                "required": True,
            }),
            "company": forms.TextInput(attrs={
                "class": "input input-bordered w-full bg-base-100 text-base-content focus:input-primary transition-all duration-200",
                "placeholder": "Entreprise (optionnel)",
            }),
            "email": forms.EmailInput(attrs={
                "class": "input input-bordered w-full bg-base-100 text-base-content focus:input-primary transition-all duration-200",
                "placeholder": "Votre adresse e-mail *",
                "required": True,
            }),
            "phone": forms.TextInput(attrs={
                "class": "input input-bordered w-full bg-base-100 text-base-content focus:input-primary transition-all duration-200",
                "placeholder": "+225 07 09 779 787 *",
                "required": True,
            }),
            "service": forms.Select(attrs={
                "class": "select select-bordered w-full bg-base-100 text-base-content focus:select-primary transition-all duration-200",
                "required": True,
            }),
            "message": forms.Textarea(attrs={
                "class": "textarea textarea-bordered w-full bg-base-100 text-base-content focus:textarea-primary h-32 transition-all duration-200",
                "placeholder": "Décrivez votre projet, vos besoins informatiques ou votre demande de devis...",
                "required": True,
            }),
        }

    def clean_website(self):
        val = self.cleaned_data.get("website")
        if val:
            raise forms.ValidationError("Spam détecté.")
        return val

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        # Nettoyage des espaces et tirets
        clean_num = re.sub(r"[\s\-\.\(\)]", "", phone)
        if len(clean_num) < 8:
            raise forms.ValidationError("Veuillez saisir un numéro de téléphone valide.")
        return phone
