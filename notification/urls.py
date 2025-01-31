from django.urls import path
from .views import (
    mark_notification_as_read,
    notification_list,
    notification_create,
    notification_update,
    notification_delete,
)

app_name = "notification"

urlpatterns = [
    path(
        "notifications/mark-as-read/<int:notification_id>/",
        mark_notification_as_read,
        name="mark_notification_as_read",
    ),
    path(
        "notifications/mark-as-read/",
        mark_notification_as_read,
        name="mark_all_notifications_as_read",
    ),
    path("notification/", notification_list, name="notification_list"),
    path("create/", notification_create, name="notification_create"),
    path("<int:pk>/update/", notification_update, name="notification_update"),
    path("<int:pk>/delete/", notification_delete, name="notification_delete"),
]
