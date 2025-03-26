from django.contrib import admin
from .models import Task, SubTask, TimeLog, Holiday

admin.site.register(Task)
admin.site.register(SubTask)
admin.site.register(TimeLog)
admin.site.register(Holiday)

# Register your models here.
