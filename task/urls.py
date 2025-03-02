from django.urls import path
from .views import (
    create_or_edit_task,
    list_tasks,
    delete_task,
    user_list_tasks,
    update_task_status,
    user_detail_tasks,
    update_sub_task_status,
    manager_list_tasks,
    time_log_list,
    holiday_list,
    holiday_create,
    holiday_delete,
    holiday_edit,
    render_calendar,
)


app_name = "task"

urlpatterns = [
    path("tasks/", list_tasks, name="task_list"),
    path("task/create/", create_or_edit_task, name="create_task"),
    path("task/edit/<int:task_id>/", create_or_edit_task, name="edit_task"),
    path("task/delete/<int:task_id>/", delete_task, name="delete_task"),
    path("task/detail/<int:task_id>/", user_detail_tasks, name="user_detail_tasks"),
    path("user_tasks/", user_list_tasks, name="user_task_list"),
    path(
        "task/update-status/<int:task_id>/",
        update_task_status,
        name="update_task_status",
    ),
    path(
        "sub_task/update-status/<int:task_id>/",
        update_sub_task_status,
        name="update_sub_task_status",
    ),
    path(
        "manager/employee/tasks/", manager_list_tasks, name="manager_employee_task_list"
    ),
    path("time-logs/", time_log_list, name="time_log_list"),
    path("holidays/", holiday_list, name="holiday_list"),
    path("holidays/create/", holiday_create, name="create_holiday"),
    path("holiday/edit/<int:holiday_id>/", holiday_edit, name="edit_holiday"),
    path("holiday/delete/<int:holiday_id>/", holiday_delete, name="delete_holiday"),
    path("calendar/", render_calendar, name="calendar"),
]
