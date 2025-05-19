from django import forms
from django.forms.models import inlineformset_factory
from .models import Task, SubTask, User, Holiday, Category


class TaskForm(forms.ModelForm):

    due_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "due_date",
            "status",
            "assigned_to",
            "category",
            "priority",
            "file",
        ]
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}

    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.none(),  # Placeholder, will be updated in the view
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)  # Get the logged-in user from kwargs
        assigned_to_list = kwargs.pop(
            "assigned_to_list", None
        )  # Get the assigned_to_list from kwargs

        super().__init__(*args, **kwargs)

        # If assigned_to_list is provided, set the queryset for the 'assigned_to' field
        if assigned_to_list is not None:
            self.fields["assigned_to"].queryset = assigned_to_list

        # Update the widget for all fields to add form-control class
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


# Define SubTaskForm before using it in the formset
class SubTaskForm(forms.ModelForm):
    class Meta:
        model = SubTask
        fields = ["title", "description", "status", "file"]

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
        fields = ["status", "task_upload_file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap class to the status field
        self.fields["status"].widget.attrs.update({"class": "form-control"})
        self.fields["task_upload_file"].widget.attrs.update({"class": "form-control"})


class SubTaskStatusForm(forms.ModelForm):
    class Meta:
        model = SubTask
        fields = ["status", "task_upload_file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap class to the status field
        self.fields["status"].widget.attrs.update({"class": "form-control"})
        self.fields["task_upload_file"].widget.attrs.update({"class": "form-control"})


class HolidayForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), label="Date")

    class Meta:
        model = Holiday
        fields = ["date", "title"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class HolidayForm(forms.Form):
    title = forms.CharField(max_length=255, label="Title")
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), label="Start Date"
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), label="End Date"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class HolidayUpdateForm(forms.ModelForm):
    class Meta:
        model = Holiday
        fields = [
            "title",
            "date",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
