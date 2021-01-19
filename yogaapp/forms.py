from django import forms
from .models import SettingPlanModel

class CreateSettingPlanForm(forms.ModelForm):
    class Meta:
        model = SettingPlanModel
        fields = ('name', 'price', 'location', 'max_book', 'memo', 'image')