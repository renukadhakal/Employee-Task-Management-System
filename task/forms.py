from django import forms
from django.forms.models import inlineformset_factory
from .models import Task, SubTask


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "due_date", "status", "assigned_to"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})


class SubTaskForm(forms.ModelForm):
    class Meta:
        model = SubTask
        fields = ["title", "description", "due_date", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})


# Inline formset for SubTask under a Task
SubTaskFormSet = inlineformset_factory(
    Task,
    SubTask,
    form=SubTaskForm,
    extra=0,  # Number of extra empty forms to display
    can_delete=True,  # Allow deleting sub-tasks
)


class TaskStatusForm(forms.ModelForm): 
    class Meta:
        model = Task
        fields = ["status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap class to the status field
        self.fields["status"].widget.attrs.update({"class": "form-control"})


class SubTaskStatusForm(forms.ModelForm):
    class Meta:
        model = SubTask
        fields = ["status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap class to the status field
        self.fields["status"].widget.attrs.update({"class": "form-control"})
