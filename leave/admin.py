from django.contrib import admin
from .models import LeaveType, LeaveRequest

admin.site.register(LeaveType)
admin.site.register(LeaveRequest)
