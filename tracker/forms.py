from django import forms
from django.contrib.auth.models import User

from .models import FarmProject, FarmTask, FarmTaskProgressUpdate, Field, FieldRecord, UserProfile


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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = User.objects.filter(
            userprofile__role=UserProfile.FIELD_WORKER
        )

    class Meta:
        model = FarmTask
        fields = ["project", "title", "description", "assigned_to", "due_date", "status", "priority", "image"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }


class FarmTaskCompletionForm(forms.ModelForm):
    status = forms.ChoiceField(choices=[
        ("IN_PROGRESS", "In Progress"),
        ("DONE", "Done"),
    ])

    class Meta:
        model = FarmTaskProgressUpdate
        fields = ["status", "comment", "image"]
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 4}),
        }


class FieldRecordForm(forms.ModelForm):
    class Meta:
        model = FieldRecord
        fields = ["field", "project", "crop", "crop_stage", "advice"]
