from django import forms


class ContactForm(forms.Form):
    required_error = {"required": "Ce champ est obligatoire."}
    name = forms.CharField(label="Nom", max_length=120, error_messages=required_error)
    email = forms.EmailField(
        label="Adresse e-mail",
        error_messages={**required_error, "invalid": "Saisissez une adresse e-mail valide."},
    )
    subject = forms.CharField(label="Sujet", max_length=160, error_messages=required_error)
    message = forms.CharField(
        label="Message", widget=forms.Textarea(attrs={"rows": 7}), error_messages=required_error
    )
    consent = forms.BooleanField(
        label="J’accepte que mes informations soient utilisées pour répondre à ma demande.",
        error_messages=required_error,
    )
    website = forms.CharField(
        required=False,
        label="Site web",
        widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
    )
