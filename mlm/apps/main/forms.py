from django import forms
from .models import MLMConfig


class MLMConfigForm(forms.ModelForm):
    class Meta:
        model = MLMConfig
        fields = "__all__"
