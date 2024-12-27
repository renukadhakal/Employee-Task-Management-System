from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control"}))
    password = forms.CharField(label="Password",widget=forms.PasswordInput(attrs={"class":"form-control"}))

    class Meta:
        model = User
        fields = "__all__"