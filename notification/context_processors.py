from .models import Notification


# Create your views here.
def notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user)
        no_of_unread = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
        return {"notifications": notifications, "no_of_unread": no_of_unread}
    return {"notifications": [], "no_of_unread": 0}
