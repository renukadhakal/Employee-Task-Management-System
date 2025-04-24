from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordChangeForm,
)
from .models import User
from django.core.exceptions import ValidationError
import re


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(
        label="Password", widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = "__all__"


class UserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Password"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Confirm Password",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "image",
            "password1",
            "password2",
        ]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        # Validate that both passwords match
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Passwords do not match.")

        # Optional: Add custom password strength validation
        if password1 and len(password1) < 8:
            self.add_error("password1", "Password must be at least 8 characters long.")
        if password1 and not any(char.isdigit() for char in password1):
            self.add_error("password1", "Password must contain at least one number.")
        if password1 and not any(char.isalpha() for char in password1):
            self.add_error("password1", "Password must contain at least one letter.")
        if password1 and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password1):
            self.add_error(
                "password1",
                "Password must contain at least one special character (e.g., @, #, $, %, etc.).",
            )

        return cleaned_data

    def save(self, commit=True):
        """
        Save the user, validate password, and hash it before saving.
        """
        user = super().save(commit=False)  # Save user without committing to DB
        user.set_password(self.cleaned_data["password1"])  # Hash the password
        if commit:
            user.save()  # Commit to DB
        return user


class EmployeeTransferForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=User.objects.filter(role=User.Role_Type.EMPLOYEE),
        label="Select Employee",
    )
    new_manager = forms.ModelChoiceField(
        queryset=User.objects.filter(role=User.Role_Type.MANAGER),
        label="Select New Manager",
    )


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "role", "image"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter current password"}
        ),
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter new password"}
        ),
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm new password"}
        ),
    )


class ForgetpasswordForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)


class OTPVerifivationForm(forms.Form):
    otp = forms.CharField(label="OTP", max_length=6)


class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("new_password") != cleaned_data.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match. ")
        return cleaned_data
