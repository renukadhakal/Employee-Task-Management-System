from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "other",
            {
                "fields": (
                    
                    "image",
                    "role",
                    
                ),
            },
        ),
    )
