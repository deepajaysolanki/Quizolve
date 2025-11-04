# myapp/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin 
from .models import AppUsers, UserQuizAttempt, AnsweredQuestion

# --- 1. Admin Configuration for your Custom User ---
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
    
# --- 2. Admin Configuration for Quiz Attempts ---
@admin.register(UserQuizAttempt)
class UserQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz_identifier', 'quiz_type', 'score', 'total_questions', 'created_at')
    list_filter = ('quiz_type', 'created_at', 'quiz_identifier')
    search_fields = ('user__email', 'quiz_identifier')
    
    # This adds a "Delete selected attempts" action to the list view
    actions = ['delete_selected']

# --- 3. (Optional) Admin Configuration for All Answers ---
# This lets you see every answer to every quiz
@admin.register(AnsweredQuestion)
class AnsweredQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'user_answer', 'is_correct', 'attempt')
    list_filter = ('is_correct',)

# --- 4. Register your User model ---
# Unregister the default User if it's still registered (sometimes needed)
# admin.site.unregister(User) 
admin.site.register(AppUsers, CustomUserAdmin)
