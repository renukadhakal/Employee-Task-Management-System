from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from .models import Notification
from django.shortcuts import render, get_object_or_404, redirect
from .models import Notification
from .forms import NotificationForm
from django.contrib import messages


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


def notification_list(request):
    notifications = Notification.objects.all().order_by("-id")
    return render(request, "notifications/list.html", {"notifications": notifications})


def notification_create(request):
    if request.method == "POST":
        form = NotificationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Notification created successfully!")
            return redirect("notification_list")
    else:
        form = NotificationForm()
    return render(request, "notifications/form.html", {"form": form})


def notification_update(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    if request.method == "POST":
        form = NotificationForm(request.POST, instance=notification)
        if form.is_valid():
            form.save()
            messages.success(request, "Notification updated successfully!")
            return redirect("notification_list")
    else:
        form = NotificationForm(instance=notification)
    return render(request, "notifications/form.html", {"form": form})


def notification_delete(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    if request.method == "POST":
        notification.delete()
        messages.success(request, "Notification deleted successfully!")
        return redirect("notification_list")
    return render(
        request, "notifications/confirm_delete.html", {"notification": notification}
    )
