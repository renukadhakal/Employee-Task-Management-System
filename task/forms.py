from django import forms
from django.forms.models import inlineformset_factory
from .models import Task, SubTask, User


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "due_date", "status", "assigned_to"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)  # Get the logged-in user from kwargs
        super().__init__(*args, **kwargs)

        if user:
            if user.role == User.Role_Type.ADMIN:
                self.fields["assigned_to"].queryset = User.objects.all()
            elif user.role == User.Role_Type.MANAGER:
                self.fields["assigned_to"].queryset = User.objects.filter(
                    report_to=user
                )

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


# Define SubTaskForm before using it in the formset
class SubTaskForm(forms.ModelForm):
    class Meta:
        model = SubTask
        fields = ["title", "description", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


# Inline formset for SubTask under a Task
SubTaskFormSet = inlineformset_factory(
    Task,
    SubTask,
    form=SubTaskForm,  # Now SubTaskForm is properly defined
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
