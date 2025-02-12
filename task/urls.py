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
]
