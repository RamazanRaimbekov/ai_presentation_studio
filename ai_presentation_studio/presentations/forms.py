from django import forms
from django.core.validators import RegexValidator


PALETTE_OPTIONS = [
    {"value": "red", "label": "Red / Black", "bg": "#0B0B0D", "accent": "#E10600", "text": "#FFFFFF"},
    {"value": "mono", "label": "Black / White", "bg": "#0B0B0D", "accent": "#FFFFFF", "text": "#FFFFFF"},
    {"value": "ocean", "label": "Ocean Blue", "bg": "#07131F", "accent": "#2F80FF", "text": "#F7FAFF"},
    {"value": "emerald", "label": "Emerald", "bg": "#071411", "accent": "#44F3A4", "text": "#F4FFF9"},
    {"value": "violet", "label": "Violet", "bg": "#120B1B", "accent": "#B56CFF", "text": "#F9F5FF"},
    {"value": "sunset", "label": "Sunset", "bg": "#180C08", "accent": "#FF6B35", "text": "#FFF8F4"},
    {"value": "custom", "label": "Custom", "bg": "#111111", "accent": "#FF0000", "text": "#FFFFFF"},
]

PALETTE_CHOICES = [(item["value"], item["label"]) for item in PALETTE_OPTIONS]
LANGUAGES = [("uz", "O‘zbekcha"), ("ru", "Русский"), ("en", "English")]
HEX_VALIDATOR = RegexValidator(r"^#[0-9A-Fa-f]{6}$", "Rang #RRGGBB formatida bo‘lishi kerak.")


class PresentationForm(forms.Form):
    prompt = forms.CharField(
        label="Prezentatsiya mavzusi",
        widget=forms.Textarea(
            attrs={
                "rows": 7,
                "placeholder": "Masalan: Prompt Engineering haqida 10 slaydli, hayotiy misollar bilan prezentatsiya...",
            }
        ),
        min_length=10,
    )
    slide_count = forms.IntegerField(label="Slaydlar", min_value=3, max_value=20, initial=10)
    language = forms.ChoiceField(label="Til", choices=LANGUAGES, initial="uz")
    color_preset = forms.ChoiceField(
        label="Prezentatsiya ranglari",
        choices=PALETTE_CHOICES,
        initial="red",
        widget=forms.HiddenInput(),
    )
    background_color = forms.CharField(
        label="Background",
        initial="#111111",
        validators=[HEX_VALIDATOR],
        widget=forms.TextInput(attrs={"type": "color"}),
    )
    accent_color = forms.CharField(
        label="Accent",
        initial="#FF0000",
        validators=[HEX_VALIDATOR],
        widget=forms.TextInput(attrs={"type": "color"}),
    )
    text_color = forms.CharField(
        label="Text",
        initial="#FFFFFF",
        validators=[HEX_VALIDATOR],
        widget=forms.TextInput(attrs={"type": "color"}),
    )
