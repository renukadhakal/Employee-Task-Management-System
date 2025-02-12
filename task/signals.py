from django.core.mail import send_mail
from django.conf import settings
from .models import Task
from notification.models import Notification
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Task)
def send_notification_on_task(sender, instance, created, **kwargs):
    if created:
        # Create a notification in the system
        Notification.objects.create(
            title="New Task Assigned",
            message=instance.title,
            user=instance.assigned_to,
        )

        # Send email notification
        subject = "New Task Assigned to You"
        message = (
            f"Dear {instance.assigned_to.username},\n\n"
            f"A new task has been assigned to you:\n\n"
            f"Task Title: {instance.title}\n"
            f"Description: {instance.description}\n\n"
            "Please log in to your account to check the details.\n\n"
            "Best regards,\n"
            "The ETMS Team"
        )
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [instance.assigned_to.email]

        if instance.assigned_to.email:
            send_mail(subject, message, email_from, recipient_list)
