from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserLoginForm
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import UserCreationForm, UserUpdateForm, CustomPasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User
from django.urls import reverse_lazy
from .services.send_registration_mail import send_registration_email


# Create your views here.
def userLogin(request):
    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.first_time:
                    return redirect("account:change_password")
                return redirect("account:home")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = UserLoginForm()
    return render(request, "account/login.html", {"form": form})


@login_required(login_url="/login")
def index(request):
    return render(request, "index.html")


def userLogout(request):
    logout(request)
    return redirect("account:home")


class AdminUserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "users/admin_user_list.html"
    context_object_name = "users"


class AdminUserCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = UserCreationForm
    template_name = "users/manager_user_form.html"
    success_url = reverse_lazy("account:admin-user-list")

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.instance
        send_registration_email(
            user.email, user.username, form.cleaned_data["password1"]
        )
        return response


class AdminUserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "users/manager_user_form.html"
    success_url = reverse_lazy("account:manager-user-list")


def delete_user_admin(request, id):
    user = get_object_or_404(User, id=id)
    user.delete()
    return redirect("account:manager-user-list")


class ManagerUserListView(LoginRequiredMixin, ListView):
    model = User
    # queryset = User.objects.filter(role="employee" )
    template_name = "users/manager_user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        return User.objects.filter(role="employee", report_to=self.request.user)


class ManagerUserCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = UserCreationForm
    template_name = "users/manager_user_form.html"
    success_url = reverse_lazy("account:manager-user-list")

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            raise ValueError("The user is not authenticated.")

        employee = form.save(commit=False)
        employee.report_to = self.request.user
        employee.save()

        # Send registration email
        send_registration_email(
            employee.email, employee.username, form.cleaned_data["password1"]
        )

        # Use the standard CreateView success flow
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("account:manager-user-list")


class ManagerUserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "users/manager_user_form.html"
    success_url = reverse_lazy("account:manager-user-list")


def delete_user_manager(request, id):
    user = get_object_or_404(User, id=id)
    user.delete()
    return redirect("account:manager-user-list")


@login_required(login_url="/login")
def change_password(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            user.first_time = False
            user.save()
            messages.success(request, "Your password was successfully updated!")
            return redirect("/")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, "account/change_password.html", {"form": form})


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "users/user_update_form.html"
    success_url = reverse_lazy("account:home")
