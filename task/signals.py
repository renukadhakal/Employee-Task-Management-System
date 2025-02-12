from .models import Task
from notification.models import Notification
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Task)
def send_notification_on_task(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            title="New Task Have been assigned to you",
            message=instance.title,
            user=instance.assigned_to,
        )
