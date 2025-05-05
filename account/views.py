from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserLoginForm
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import (
    UserCreationForm,
    UserUpdateForm,
    CustomPasswordChangeForm,
    EmployeeTransferForm,
    ForgetpasswordForm,
    OTPVerifivationForm,
    SetNewPasswordForm,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User
from django.urls import reverse_lazy
from .services.send_registration_mail import send_registration_email
from task.models import Task
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Count, Sum, F, ExpressionWrapper, fields, Q
from django.db.models.functions import TruncMonth
from django.utils.timezone import now

import json
from task.models import Task, TimeLog
from leave.models import LeaveRequest


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
    return redirect("task:dashboard")


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


@login_required(login_url="/login")
def transfer_employee(request):
    if request.method == "POST":
        form = EmployeeTransferForm(request.POST)
        if form.is_valid():
            employee = form.cleaned_data["employee"]
            new_manager = form.cleaned_data["new_manager"]

            old_manager = employee.report_to

            employee.report_to = new_manager
            employee.save()

            Task.objects.filter(created_by=employee, assigned_to=employee).update(
                created_by=new_manager
            )

            messages.success(
                request,
                f"{employee.username} has been transferred from {old_manager} to {new_manager}, and tasks have been updated.",
            )
            return redirect("account:transfer_employee")
    else:
        form = EmployeeTransferForm()

    return render(request, "account/transfer_employee.html", {"form": form})


def get_month_range(start_date, end_date):
    result = {}
    current = start_date.replace(day=1)
    while current <= end_date:
        result[current.strftime("%Y-%m")] = 0
        current += relativedelta(months=1)
    return result


@login_required(login_url="/login")
def get_user_profile(request, pk):
    user = get_object_or_404(User, pk=pk)

    # Task Data
    tasks = Task.objects.filter(
        assigned_to=user, status="COMPLETED", completed_at__isnull=False
    )
    task_data = []
    for task in tasks:
        if task.completed_at and task.created_at:
            days_taken = (task.completed_at.date() - task.created_at.date()).days
            overdue_days = 0
            if task.due_date and task.completed_at.date() > task.due_date:
                overdue_days = (task.completed_at.date() - task.due_date).days

            task_data.append(
                {
                    "title": task.title,
                    "days_taken": days_taken,
                    "overdue_days": overdue_days,
                }
            )

    # Date range: last 3 full months including current
    today = datetime.now().date()
    start_date = today.replace(day=1) - relativedelta(months=2)
    end_date = today

    month_range = get_month_range(start_date, end_date)

    # Leave Data
    leave_queryset = LeaveRequest.objects.filter(
        user=user, end_at__gte=start_date, start_at__lte=end_date
    )
    leave_data = (
        leave_queryset.annotate(month=TruncMonth("start_at"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    leave_map = month_range.copy()
    for entry in leave_data:
        label = entry["month"].strftime("%Y-%m")
        leave_map[label] = entry["count"]

    leave_labels = list(leave_map.keys())
    leave_values = list(leave_map.values())

    # TimeLog Data
    time_queryset = TimeLog.objects.filter(
        user=user, end_time__gte=start_date, start_time__lte=end_date
    )
    time_data = (
        time_queryset.annotate(
            duration=ExpressionWrapper(
                F("end_time") - F("start_time"), output_field=fields.DurationField()
            ),
            month=TruncMonth("start_time"),
        )
        .values("month")
        .annotate(total_hours=Sum("duration"))
        .order_by("month")
    )

    time_map = month_range.copy()
    for entry in time_data:
        label = entry["month"].strftime("%Y-%m")
        hours = (
            entry["total_hours"].total_seconds() / 3600 if entry["total_hours"] else 0
        )
        time_map[label] = round(hours, 2)

    time_labels = list(time_map.keys())
    time_values = list(time_map.values())

    context = {
        "employee": user,
        "task_data": task_data,
        "leave_labels": json.dumps(leave_labels),
        "leave_values": json.dumps(leave_values),
        "time_labels": json.dumps(time_labels),
        "time_values": json.dumps(time_values),
        "start_date": json.dumps(start_date.strftime("%Y-%m-%d")),
        "end_date": json.dumps(end_date.strftime("%Y-%m-%d")),
    }

    workload_summary = Task.objects.filter(
        assigned_to=user, status__in=["PENDING", "IN_PROGRESS", "ON_HOLD"]
    ).aggregate(
        total_tasks=Count("id"),
        high_priority=Count("id", filter=Q(priority="HIGH")),
        overdue=Count("id", filter=Q(due_date__lt=now().date())),
    )

    context.update(
        {
            "workload_labels": json.dumps(["Total Tasks", "High Priority", "Overdue"]),
            "workload_values": json.dumps(
                [
                    workload_summary["total_tasks"] or 0,
                    workload_summary["high_priority"] or 0,
                    workload_summary["overdue"] or 0,
                ]
            ),
        }
    )

    return render(request, "account/user_profile.html", context)


import random
from ETMS.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from django.utils import timezone


def generate_email_otp():
    return random.randint(100000, 999999)


def forget_password_view(request):
    if request.method == "POST":
        form = ForgetpasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=email)
                otp = generate_email_otp()
                user.email_otp = otp
                user.save()
                send_mail(
                    "Your OTP Code", f"Your OTP is {otp}", EMAIL_HOST_USER, [email]
                )
                request.session["reset_email"] = email
                messages.success(request, "OTP has been sent to your email.")
                return redirect("account:verify_otp")
            except User.DoesNotExist:
                messages.error(request, "No account found with this email.")
    else:
        form = ForgetpasswordForm()

    return render(request, "account/forgot_password.html", {"form": form})


def verify_otp_view(request):
    email = request.session.get("reset_email")
    if not email:
        return redirect("forgot_password")

    user = get_object_or_404(User, email=email)

    if request.method == "POST":
        form = OTPVerifivationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data["otp"]
            if user.email_otp == int(otp):
                return redirect("account:set_new_password")
            else:
                messages.error(request, "Invalid or expired OTP.")
    else:
        form = OTPVerifivationForm()
    return render(request, "account/verify_otp.html", {"form": form})


def set_new_password_view(request):
    email = request.session.get("reset_email")
    if not email:
        return redirect("forgot_password")

    user = get_object_or_404(User, email=email)

    if request.method == "POST":
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data["new_password"]
            user.set_password(password)
            user.email_otp = 0
            user.save()
            messages.success(request, "Password changed successfully. Please login.")
            return redirect("account:login")
    else:
        form = SetNewPasswordForm()
    return render(request, "account/set_new_password.html", {"form": form})
