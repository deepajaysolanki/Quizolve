# myapp/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AppUsers

class CustomUserAdmin(UserAdmin):
    # These settings MUST use fields that exist on your AppUsers model
    list_display = ('email', 'is_staff', 'is_active', 'last_login')
    ordering = ('email',)
    
    # The rest of your configuration
    list_filter = ('is_staff', 'is_active',)
    search_fields = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_of_birth')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password2'),
        }),
    )
    def get_queryset(self, request):
        # Get the original list of all users
        qs = super().get_queryset(request)
        # Return a new, filtered list that ONLY includes users with the role 'user'
        return qs.filter(role='user')

admin.site.register(AppUsers, CustomUserAdmin)
# ... your other unregister calls