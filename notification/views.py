from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from .models import Notification


def mark_notification_as_read(request, notification_id=None):
    if request.user.is_authenticated:
        if notification_id:  # Mark a specific notification as read
            notification = get_object_or_404(
                Notification, id=notification_id, user=request.user
            )
            notification.is_read = True
            notification.save()
            return JsonResponse(
                {"success": True, "message": "Notification marked as read."}
            )
        else:  # Mark all notifications as read
            Notification.objects.filter(user=request.user, is_read=False).update(
                is_read=True
            )
            return JsonResponse(
                {"success": True, "message": "All notifications marked as read."}
            )
    return JsonResponse(
        {"success": False, "message": "Unauthorized access."}, status=403
    )
