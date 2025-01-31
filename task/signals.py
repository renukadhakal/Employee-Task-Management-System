from .models import Task
from notification.models import Notification

@receiver(post_save, sender=Task)
def send_notification_on_task(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            Notification="New Task Have been assigned to you",
            message = instance.title,
            user = instance.assigned_to ,
        )