from django.contrib import admin
from .models import Notification


# Register your models here.
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "is_read", "created_at")
    search_fields = ("title", "user__username")
    list_filter = ("is_read", "created_at")
