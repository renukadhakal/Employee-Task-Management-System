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
        form = TaskStatusForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            form.save()
            return redirect("task:user_task_list")  # Redirect back to the task list
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
    holidays = [
        date.strftime("%Y-%m-%d")
        for date in list(Holiday.objects.all().values_list("date", flat=True))
    ]

    holiday_form = HolidayForm()

    return render(
        request,
        "calendar/base.html",
        {"holidays": json.dumps(holidays), "form": holiday_form},
    )


@login_required(login_url="/login")
def dashboard(request):
    start_date = request.GET.get("start_date", datetime.now().strftime("%Y-%m-%d"))
    end_date = request.GET.get(
        "end_date", (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    )

    # Set default values if dates are not provided
    if start_date and end_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    else:
        start_date = None
        end_date = None
    if request.user.role == User.Role_Type.ADMIN:
        leave_queryset = LeaveRequest.objects.all()
        time_queryset = TimeLog.objects.all()
    elif request.user.role == User.Role_Type.MANAGER:
        leave_queryset = LeaveRequest.objects.filter(user__report_to=request.user)
        time_queryset = TimeLog.objects.filter(user__report_to=request.user)
    else:
        time_queryset = TimeLog.objects.filter(user=request.user)
        leave_queryset = LeaveRequest.objects.filter(user=request.user)

    if start_date and end_date:
        leave_queryset = leave_queryset.filter(
            start_at__gte=start_date, end_at__lte=end_date
        )

    leave_data = (
        leave_queryset.extra({"day": "date(start_at)"})
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    print(leave_data, "leave data")
    leave_labels = [entry["day"] for entry in leave_data]
    leave_values = [entry["count"] for entry in leave_data]

    # Filter and clean Time Logs data

    if start_date and end_date:
        time_queryset = time_queryset.filter(
            start_time__gte=start_date, end_time__lte=end_date
        )

    time_data = (
        time_queryset.annotate(
            duration=ExpressionWrapper(
                F("end_time") - F("start_time"), output_field=fields.DurationField()
            )
        )
        .extra({"day": "date(start_time)"})
        .values("day")
        .annotate(total_hours=Sum("duration"))
        .order_by("day")
    )
    print(time_data, "time data")
    time_labels = [entry["day"] for entry in time_data]
    time_values = [
        entry["total_hours"].total_seconds() / 3600 if entry["total_hours"] else 0
        for entry in time_data
    ]
    context = {
        "leave_labels": leave_labels,
        "leave_values": leave_values,
        "time_labels": time_labels,
        "time_values": time_values,
        "start_date": start_date,
        "end_date": end_date,
    }
    # context = {
    #     "leave_labels": json.dumps(
    #         leave_labels, sort_keys=False, indent=1, cls=DateTimeEncoder
    #     ),
    #     "leave_values": json.dumps(leave_values),
    #     # "leave_values": leave_values,
    #     "time_labels": json.dumps(
    #         time_labels, sort_keys=False, indent=1, cls=DateTimeEncoder
    #     ),
    #     "time_values": json.dumps(
    #         time_values, sort_keys=False, indent=1, cls=DateTimeEncoder
    #     ),
    #     "start_date": start_date.strftime("%Y-%m-%d") if start_date else "",
    #     "end_date": end_date.strftime("%Y-%m-%d") if end_date else "",
    # }

    print(context, "context")

    return render(
        request, "account/dashboard.html", json.dumps(context, cls=DateTimeEncoder)
    )


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
