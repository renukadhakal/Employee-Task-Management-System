from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Task, SubTask, TimeLog, Holiday, Category
from .forms import (
    TaskForm,
    SubTaskFormSet,
    TaskStatusForm,
    SubTaskStatusForm,
    HolidayForm,
    CategoryForm,
)
from account.models import User
import json
from datetime import datetime, timedelta, date
from django.db.models import Count, Sum, F, ExpressionWrapper, fields
from leave.models import LeaveRequest
from django.http import HttpResponse
import csv
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from django.db.models.functions import TruncMonth
from collections import OrderedDict
from dateutil.relativedelta import relativedelta


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, date):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


@login_required(login_url="/login")
def create_or_edit_task(request, task_id=None):
    holidays = [
        date.strftime("%Y-%m-%d")
        for date in list(Holiday.objects.all().values_list("date", flat=True))
    ]

    if task_id:
        task = get_object_or_404(Task, id=task_id)
    else:
        task = Task(created_by=request.user)

    if request.method == "POST":
        if request.user.is_superuser:
            assigned_to_list = User.objects.all()
        else:
            assigned_to_list = User.objects.filter(
                report_to=request.user, role=User.Role_Type.EMPLOYEE
            )

        # Include request.FILES for file uploads
        task_form = TaskForm(
            request.POST,
            request.FILES,
            instance=task,
            assigned_to_list=assigned_to_list,
        )
        subtask_formset = SubTaskFormSet(request.POST, request.FILES, instance=task)

        if task_form.is_valid() and subtask_formset.is_valid():
            task = task_form.save()
            subtask_formset.save()
            return redirect("task:task_list")  # Redirect to task detail or task list

    else:
        if request.user.is_superuser:
            assigned_to_list = User.objects.all()
        else:
            assigned_to_list = User.objects.filter(
                report_to=request.user, role=User.Role_Type.EMPLOYEE
            )
        task_form = TaskForm(instance=task, assigned_to_list=assigned_to_list)
        subtask_formset = SubTaskFormSet(instance=task)

    return render(
        request,
        "task/task_form.html",
        {
            "assigned_to_list": assigned_to_list,
            "task_form": task_form,
            "subtask_formset": subtask_formset,
            "holidays": json.dumps(holidays),
        },
    )


@login_required(login_url="/login")
def list_tasks(request):
    tasks = Task.objects.all().order_by("-due_date")
    return render(request, "task/task_list.html", {"tasks": tasks})


@login_required(login_url="/login")
def manager_list_tasks(request):
    user = request.user
    tasks = Task.objects.filter(assigned_to__report_to=user).order_by("-due_date")
    return render(request, "task/task_list.html", {"tasks": tasks})


@login_required(login_url="/login")
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, created_by=request.user)

    task.delete()

    return redirect("task:task_list")  # Redirect to task detail or task list


@login_required(login_url="/login")
def user_list_tasks(request):
    tasks = Task.objects.filter(assigned_to=request.user).order_by("-due_date")
    return render(request, "task/user_task_list.html", {"tasks": tasks})


@login_required(login_url="/login")
def user_detail_tasks(request, task_id):
    task = Task.objects.get(assigned_to=request.user, id=task_id)
    sub_task = SubTask.objects.filter(task=task)
    return render(
        request, "task/user_task_detail.html", {"tasks": task, "sub_task": sub_task}
    )


@login_required(login_url="/login")
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)

    if request.method == "POST":
        form = TaskStatusForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            if request.user.Role_Type.EMPLOYEE:
                if task.status == "IN_PROGRESS":
                    log, created = TimeLog.objects.get_or_create(
                        user=request.user, task=task
                    )
                    log.start_time = timezone.now()
                    log.save()
                if task.status == "COMPLETED":
                    log = TimeLog.objects.get(user=request.user, task=task)
                    log.end_time = timezone.now()
                    log.save()
            return redirect("task:user_task_list")
    else:
        form = TaskStatusForm(instance=task)

    return render(request, "task/update_task_status.html", {"form": form, "task": task})


@login_required(login_url="/login")
def update_sub_task_status(request, task_id):
    subtask = get_object_or_404(SubTask, id=task_id)

    if request.method == "POST":
        form = SubTaskStatusForm(request.POST, request.FILES, instance=subtask)
        if form.is_valid():
            form.save()
            return redirect("task:user_task_list")  # Redirect back to the task list
    else:
        form = SubTaskStatusForm(instance=subtask)

    return render(
        request, "task/update_task_status.html", {"form": form, "task": subtask}
    )


@login_required(login_url="/login")
def time_log_list(request):

    user = request.user
    if user.role == User.Role_Type.ADMIN:
        logs = TimeLog.objects.all().order_by("-task__due_date")
    elif user.role == User.Role_Type.MANAGER:
        logs = TimeLog.objects.filter(task__created_by=user).order_by("-task__due_date")
    else:
        logs = TimeLog.objects.filter(user=user).order_by("-task__due_date")

    if request.GET.get("start_date") and request.GET.get("end_date"):
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        logs = TimeLog.objects.filter(start_time__range=[start_date, end_date])
    logs = logs.filter(task__isnull=False)
    if len(request.GET.get("export", "")) > 0:
        print("export")
        response = HttpResponse(content_type="text/csv")
        writer = csv.writer(response)
        writer.writerow(
            [
                "User",
                "Task",
                "Start Time",
                "End Date",
                "Duration",
                "Priority",
                "Category",
                "Status",
            ]
        )
        for log in logs:
            writer.writerow(
                [
                    log.user.get_full_name(),
                    log.task.title,
                    log.start_time,
                    log.end_time,
                    log.get_total_time,
                    log.task.priority,
                    log.task.category.category_name if log.task.category else "N/A",
                    log.task.status,
                ]
            )
        response["Content-Disposition"] = 'attachment; filename="time_logs.csv"'
        return response
    return render(request, "timelog/log_list.html", {"logs": logs})


@login_required(login_url="/login")
def holiday_list(request):
    holidays = Holiday.objects.all()
    form = HolidayForm()
    if request.method == "POST":
        form = HolidayForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("task:holiday_list")
    return render(
        request, "holiday/holiday_list.html", {"holidays": holidays, "form": form}
    )


@login_required(login_url="/login")
def holiday_edit(request, holiday_id):
    holiday = get_object_or_404(Holiday, id=holiday_id)
    form = HolidayForm(instance=holiday)
    if request.method == "POST":
        form = HolidayForm(request.POST, instance=holiday)
        if form.is_valid():
            form.save()
            return redirect("task:holiday_list")
    return render(
        request, "holiday/holiday_edit.html", {"form": form, "holiday": holiday}
    )


@login_required(login_url="/login")
def holiday_delete(request, holiday_id):
    holiday = get_object_or_404(Holiday, id=holiday_id)
    holiday.delete()
    return redirect("task:holiday_list")


@login_required(login_url="/login")
def holiday_create(request):
    form = HolidayForm()
    if request.method == "POST":
        form = HolidayForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("task:holiday_list")
    return render(request, "holiday/holiday_create.html", {"form": form})


@login_required(login_url="/login")
def render_calendar(request):
    holidays = {
        holiday.date.strftime("%Y-%m-%d"): holiday.title
        for holiday in Holiday.objects.all()
    }

    holiday_form = HolidayForm()

    return render(
        request,
        "calendar/base.html",
        {"holidays": json.dumps(holidays), "form": holiday_form},
    )


def get_month_range(start_date, end_date):
    months = OrderedDict()
    current = start_date.replace(day=1)
    while current <= end_date:
        months[current.strftime("%Y-%m")] = 0
        current += relativedelta(months=1)
    return months


@login_required(login_url="/login")
def dashboard(request):
    today = datetime.now().date()

    # Show last 3 full months including current
    start_date = today.replace(day=1) - relativedelta(months=2)
    end_date = today

    # Allow custom date range via query params
    start_date_str = request.GET.get("start_date", start_date.strftime("%Y-%m-%d"))
    end_date_str = request.GET.get("end_date", end_date.strftime("%Y-%m-%d"))

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        start_date = today.replace(day=1) - relativedelta(months=2)
        end_date = today

    if request.user.role == User.Role_Type.ADMIN:
        leave_queryset = LeaveRequest.objects.all()
        time_queryset = TimeLog.objects.all()
    elif request.user.role == User.Role_Type.MANAGER:
        leave_queryset = LeaveRequest.objects.filter(user__report_to=request.user)
        time_queryset = TimeLog.objects.filter(user__report_to=request.user)
    else:
        leave_queryset = LeaveRequest.objects.filter(user=request.user)
        time_queryset = TimeLog.objects.filter(user=request.user)

    # Overlap filtering
    leave_queryset = leave_queryset.filter(
        end_at__gte=start_date, start_at__lte=end_date
    )

    time_queryset = time_queryset.filter(
        end_time__gte=start_date, start_time__lte=end_date
    )

    # Generate a complete month list
    month_range = get_month_range(start_date, end_date)

    # Leave Data (Monthly Group)
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

    # TimeLog Data (Monthly Group)
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
        "leave_labels": json.dumps(leave_labels),
        "leave_values": json.dumps(leave_values),
        "time_labels": json.dumps(time_labels),
        "time_values": json.dumps(time_values),
        "start_date": json.dumps(start_date.strftime("%Y-%m-%d")),
        "end_date": json.dumps(end_date.strftime("%Y-%m-%d")),
    }

    return render(request, "account/dashboard.html", context)


@login_required(login_url="/login")
def category_list(request):
    form = CategoryForm()
    categories = Category.objects.all().annotate(
        task_count=Count("tasks"),
    )
    return render(
        request,
        "task/category_list.html",
        {
            "categories": categories,
            "form": form,
        },
    )


@login_required(login_url="/login")
def category_create(request):
    form = CategoryForm()
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("task:category_list")
    return render(request, "task/category_form.html", {"form": form})
