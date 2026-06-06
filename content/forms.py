from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(
        label="Name",
        max_length=120,
        required=True,
        widget=forms.TextInput(attrs={"autocomplete": "name"}),
    )
    email = forms.EmailField(
        label="E-Mail",
        required=True,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    message = forms.CharField(
        label="Nachricht",
        required=True,
        widget=forms.Textarea(attrs={"rows": 8}),
    )
