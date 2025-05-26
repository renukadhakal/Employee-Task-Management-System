from django.contrib import admin
from .models import Task, SubTask, TimeLog, Holiday, Category

admin.site.register(Task)
admin.site.register(SubTask)
admin.site.register(TimeLog)
admin.site.register(Holiday)
admin.site.register(Category)
# Register your models here.
