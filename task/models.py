from django.db import models
from account.models import User
from django.utils import timezone

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]


class Task(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("ON_HOLD", "On Hold"),
    ]
    PRIORITY = [("HIGH", "High"), ("LOW", "Low"), ("MEDIUM", "Medium")]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="tasks"
    )
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, null=2)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(blank=True, null=True)
    completed = models.BooleanField(
        default=False
    )  # Optional, since status can also indicate completion
    priority = models.CharField(max_length=20, choices=PRIORITY, default="LOW")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="tasks", null=True, blank=True
    )
    file = models.FileField(upload_to="task/", null=True, blank=True)
    task_upload_file = models.FileField(upload_to="task/", null=True, blank=True)

    def __str__(self):
        return self.title


class SubTask(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("ON_HOLD", "On Hold"),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="sub_tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    file = models.FileField(upload_to="sub_task/", null=True, blank=True)
    task_upload_file = models.FileField(upload_to="sub_task/", null=True, blank=True)

    def __str__(self):
        return f"{self.title} (Sub-task of {self.task.title})"


class TimeLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="time_logs", null=True, blank=True
    )
    sub_task = models.ForeignKey(
        SubTask,
        on_delete=models.CASCADE,
        related_name="time_logs",
        null=True,
        blank=True,
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    # duration = models.DurationField(blank=True, null=True)

    def __str__(self):
        return f"{self.task.id if self.task else self.sub_task.id} - {self.user.get_full_name()} - {self.start_time} - {self.end_time}"

    @property
    def get_total_time(self):
        print(self.start_time, "start time")
        print(self.end_time, "end time")
        if self.task:
            if self.task.status == "COMPLETED":
                total_time = self.end_time - self.start_time
            if self.task.status == "IN_PROGRESS":
                total_time = timezone.now() - self.start_time
            if self.task.status == "PENDING":
                return "Task is not started yet"
            return round(total_time.days * 24 * 3600 + total_time.seconds // 60 / 60, 2)
        if self.sub_task:
            if self.sub_task.status == "COMPLETED":
                total_time = self.end_time - self.start_time
            if self.sub_task.status == "IN_PROGRESS":
                total_time = timezone.now() - self.start_time
            if self.sub_task.status == "PENDING":
                return "Task is not started yet"
            return round(total_time.days * 24 * 3600 + total_time.seconds // 60 / 60, 2)
        return "No task or sub-task found"


class Holiday(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateField()

    def __str__(self):
        return self.title
