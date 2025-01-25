from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


def validate_five_mb_image_size(image):
    file_size = image.size
    limit_mb = 5
    if file_size > limit_mb * 1024 * 1024:
        raise ValidationError("Max allowed size of image is %s MB" % limit_mb)


class User(AbstractUser):
    class Role_Type(models.TextChoices):
        ADMIN = "admin", "Admin"
        MANAGER = "manager", "Manager"
        EMPLOYEE = "employee", "Employee"

    role = models.CharField(
        max_length=20, choices=Role_Type.choices, default=Role_Type.EMPLOYEE
    )
    image = models.ImageField(
        upload_to="user/ranks/%Y/%m/%d/",
        null=True,
        blank=True,
        validators=[validate_five_mb_image_size],
    )
    first_time = models.BooleanField(default=True)
    report_to = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_report_to",
    )
