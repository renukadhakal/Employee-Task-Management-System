from django.urls import path
from .views import mark_notification_as_read

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
]
