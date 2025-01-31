from django import forms
from .models import Notification


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ["title", "message", "user", "is_read"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(attrs={"class": "form-control"}),
            "user": forms.Select(attrs={"class": "form-control"}),
            "is_read": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
