from django import forms
from django_formwork.widgets import SearchSelect

from lab.models import Experiment


class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ["name", "description", "accelerator", "category", "status"]
        widgets = {
            "accelerator": SearchSelect,
            "category": SearchSelect,
            "status": forms.Select(attrs={"class": "select select-bordered w-full"}),
            "name": forms.TextInput(attrs={"class": "input input-bordered w-full", "placeholder": "Experiment name"}),
            "description": forms.Textarea(
                attrs={"class": "textarea textarea-bordered w-full", "rows": 4, "placeholder": "Description..."},
            ),
        }
