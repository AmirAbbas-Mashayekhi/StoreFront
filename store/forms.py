from django import forms
from .models import Promotion


class PromotionSelectionForm(forms.Form):
    promotion = forms.ModelChoiceField(
        label="Promotion", queryset=Promotion.objects.all(), required=True
    )
