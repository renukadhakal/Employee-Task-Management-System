from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    class Role_Type(models.TextChoices):
        ADMIN="admin","Admin"
        MANAGER="manager","Manager"
        EMPLOYEE="employee","Employee"
        
    role=models.CharField(max_length=20,choices=Role_Type.choices,default=Role_Type.EMPLOYEE)
    image=models.ImageField(upload_to="user/ranks/%Y/%m/%d/", null=True, blank=True)