from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from leave.models import Leave


@receiver(post_save, sender=User)
def create_leave_on_user_creation(sender, instance, created, **kwargs):
    if created:
        Leave.objects.create(user=instance, total=20)
