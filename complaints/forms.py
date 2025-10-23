from django import forms


class AdminAccessLoginForm(forms.Form):
    username_or_email = forms.CharField(label="Username or Email", max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    secret_key = forms.CharField(widget=forms.PasswordInput, label="Secret key")

    def clean(self):
        cleaned = super().clean()
        # Basic presence validation is already handled by required fields.
        return cleaned


class AdminAccessSignupForm(forms.Form):
    ROLE_CHOICES = (
        ("HOD", "HOD"),
        ("Principal", "Principal"),
    )
    username = forms.CharField(label="Username", max_length=150)
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Role")
    secret_key = forms.CharField(widget=forms.PasswordInput, label="Secret key")
