from django.db import models
from django.db.models import Sum
from account.models import User


class LeaveType(models.Model):

    class Leave_Status(models.TextChoices):
        SICK = "sick", "Sick"
        EMERGENCY = "emergency", "Emergency"
        VACATION = "vacation", "Vacation"
        UNPAID = "unpaid", "Unpaid"
        OTHER = "other", "Other"

    total = models.PositiveBigIntegerField(default=20)
    leave_type = models.CharField(
        max_length=20, choices=Leave_Status.choices, default=Leave_Status.UNPAID
    )

    def __str__(self):
        return self.leave_type.capitalize()


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
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leave_types",
    )
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    applied_at = models.DateTimeField(auto_now_add=True, null=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="manager_users_leave_requests_approved_by",
        null=True,
    )

    @property
    def total_days(self):
        return (self.end_at - self.start_at).days + 1

    @staticmethod
    def remaining_for_type(leave_type, user):
        total_leaves = LeaveRequest.objects.filter(
            user=user, leave_type=leave_type
        ).count()
        print(total_leaves, "total leaves")
        return leave_type.total - total_leaves if total_leaves < leave_type.total else 0

    @staticmethod
    def remaining_leave(user):
        total_leaves = LeaveRequest.objects.filter(user=user).count()
        return (
            LeaveType.objects.all().aggregate(Sum("total"))["total__sum"] - total_leaves
            if total_leaves
            < LeaveType.objects.all().aggregate(Sum("total"))["total__sum"]
            else 0
        )

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.leave_type} - {self.status}"
