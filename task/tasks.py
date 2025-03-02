from datetime import timedelta, date
from django.core.mail import send_mail
from task.models import Task
from notification.models import Notification

# from ETMS.celery import app
from celery import shared_task


@shared_task
def send_task_notifications():
    today = date.today()

    reminder_days = {
        "HIGH": 7,
        "MEDIUM": 3,
        "LOW": 1,
    }

    for priority, days in reminder_days.items():
        reminder_date = today + timedelta(days=days)

        tasks = Task.objects.filter(due_date=reminder_date, priority=priority)

        for task in tasks:
            message = f"Reminder: Your {priority.lower()}-priority task '{task.title}' is due in {days} day(s)!"

            Notification.objects.create(
                title=f"Task Reminder: {task.title}",
                message=message,
                user=task.assigned_to,
            )

            if task.assigned_to.email:
                send_mail(
                    subject="Task Reminder",
                    message=message,
                    from_email="your-email@example.com",
                    recipient_list=[task.assigned_to.email],
                    fail_silently=True,
                )

    print("Task notifications and emails sent successfully.")
