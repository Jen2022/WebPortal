# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .models import Sport, Team, TeamCategory, Workspace, ParentPlayer, SessionImpacts,SessionsImpactsOverview
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'fname', 'lname', 'user_type']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'fname', 'lname', 'user_type', 'workspace')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'fname', 'lname', 'user_type', 'password1', 'password2', 'workspace')}
        ),
    )
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Sport)
admin.site.register(Team)
admin.site.register(TeamCategory)
admin.site.register(Workspace)
admin.site.register(ParentPlayer)
admin.site.register(SessionsImpactsOverview)
admin.site.register(SessionImpacts)
