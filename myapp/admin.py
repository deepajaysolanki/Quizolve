# myapp/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin 
from .models import AppUsers, UserQuizAttempt, AnsweredQuestion, ContactMessage
from django.utils.html import format_html

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
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups')}),
        ('Important dates', {'fields': ('last_login', 'date_of_birth')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password2'),
        }),
    )
    # def get_queryset(self, request):
    #     # Get the original list of all users
    #     qs = super().get_queryset(request)
    #     # Return a new, filtered list that ONLY includes users with the role 'user'
    #     return qs.filter(role='user')
    
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

# --- 4. Register User model ---
# Unregister the default User if it's still registered (sometimes needed)
# admin.site.unregister(User) 
admin.site.register(AppUsers, CustomUserAdmin)

# --- 5. Admin Configuration for Contact Messages ---
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'short_message', 'created_at', 'reply_button')
    readonly_fields = ('full_name', 'email', 'message', 'created_at')

    def short_message(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    short_message.short_description = 'Message Preview'

    # Creates a "Reply via Email" button
    def reply_button(self, obj):
        return format_html(
            '<a class="button" href="mailto:{}?subject=Reply to your Inquiry&body=Hi {},%0D%0A%0D%0ARegarding your message:%0D%0A> {}%0D%0A%0D%0A" style="background-color:#4F46E5; color:white; padding:5px 10px; border-radius:5px; text-decoration:none;">Reply via Email</a>',
            obj.email,
            obj.full_name,
            obj.message[:100]
        )
    reply_button.short_description = 'Action'
    reply_button.allow_tags = True

admin.site.register(ContactMessage, ContactMessageAdmin)