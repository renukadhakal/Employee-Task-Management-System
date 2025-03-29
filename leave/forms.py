from django import forms
from .models import LeaveRequest


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ["reason", "leave_type", "start_at", "end_at"]
        widgets = {
            "reason": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "start_at": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "end_at": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "leave_type": forms.Select(attrs={"class": "form-control"}),
        }
