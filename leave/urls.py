from django.urls import path
from . import views

app_name = "leave"

urlpatterns = [
    path("list/", views.leave_request_list, name="leave_request_list"),
    path("leave_create/", views.leave_request_create, name="leave_request_create"),
    path(
        "leave_delete/<int:pk>/",
        views.leave_request_delete,
        name="leave_request_delete",
    ),
    path("edit/<int:pk>/", views.leave_request_edit, name="leave_request_edit"),
    path(
        "manager/leaves/", views.manager_leave_requests, name="manager_leave_requests"
    ),
    path(
        "leaves_approve/<int:pk>/",
        views.approve_leave_request,
        name="approve_leave_request",
    ),
    path(
        "leaves_reject/<int:pk>/",
        views.reject_leave_request,
        name="reject_leave_request",
    ),
]
