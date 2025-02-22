from django.db import models
from account.models import User


class Leave(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users_leave")
    total = models.PositiveBigIntegerField(default=20)


class LeaveRequest(models.Model):

    class Leave_Types(models.TextChoices):
        APPROVED = "approved", "Aprroved"
        PENDING = "pending", "Pending"
        REJECTED = "rejected", "Rejected"

    status = models.CharField(
        max_length=20, choices=Leave_Types.choices, default=Leave_Types.PENDING
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="users_leave_requests"
    )
    reason = models.TextField()
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    applied_at = models.DateTimeField(auto_now_add=True, null=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="manager_users_leave_requests_approved_by",
        null=True,
    )
