# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'fname', 'lname', 'user_type']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type', 'fname', 'lname')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('user_type', 'fname', 'lname')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
