from django import forms
from .models import Promotion

from unfold.widgets import UnfoldAdminSelectWidget


class PromotionSelectionForm(forms.Form):
    promotion = forms.ModelChoiceField(
        label="Promotion",
        queryset=Promotion.objects.all(),
        required=True,
        widget=UnfoldAdminSelectWidget,
    )
