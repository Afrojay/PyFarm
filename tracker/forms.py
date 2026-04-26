from django import forms
from .models import FarmProject, FarmTask, Field


class FieldForm(forms.ModelForm):
    class Meta:
        model = Field
        fields = ["name", "crop_type", "size_acres", "location"]


class FarmProjectForm(forms.ModelForm):
    class Meta:
        model = FarmProject
        fields = ["title", "description", "field", "start_date", "end_date", "status"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class FarmTaskForm(forms.ModelForm):
    class Meta:
        model = FarmTask
        fields = ["project", "title", "description", "assigned_to", "due_date", "status", "priority"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }