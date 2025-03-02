from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Task, SubTask, TimeLog, Holiday
from .forms import TaskForm, SubTaskFormSet, TaskStatusForm, SubTaskStatusForm, HolidayForm
from account.models import User
import json


@login_required(login_url="/login")
def create_or_edit_task(request, task_id=None):
    holidays = [date.strftime("%Y-%m-%d") for date in list(Holiday.objects.all().values_list('date', flat=True))]

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
