# myapp/admin.py
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin 
from .models import AppUsers, UserQuizAttempt, AnsweredQuestion, ContactMessage, PaymentRequest
from django.utils.html import format_html
from datetime import date, timedelta

# --- 1. Admin Configuration for your Custom User ---
class CustomUserAdmin(UserAdmin):
    # These settings MUST use fields that exist on your AppUsers model
    list_display = ('email', 'is_staff', 'is_active', 'is_premium', 'subscription_expiry', 'last_login')
    ordering = ('email',)
    
    # The rest of configuration
    list_filter = ('is_staff', 'is_active', 'is_premium')
    search_fields = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'profile_photo')}),
        ('Subscription', {'fields': ('is_premium', 'subscription_expiry')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'first_name', 'last_name', 'profile_photo'),
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

# --- 6. Admin Configuration for Payment Requests ---
class PaymentRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan_type', 'amount', 'transaction_id', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'plan_type', 'created_at')
    search_fields = ('user__email', 'transaction_id')
    ordering = ('-created_at',) 
    actions = ['approve_payment']

    # --- 1. LOGIC FOR "SAVE" BUTTON ---
    def save_model(self, request, obj, form, change):
        # If the admin checks the box and clicks "Save"
        if 'is_approved' in form.changed_data and obj.is_approved:
            self.perform_upgrade(request, obj)
            messages.success(request, f"User {obj.user.email} has been upgraded!")
        
        super().save_model(request, obj, form, change)

    # --- 2. LOGIC FOR DROPDOWN ACTION ---
    def approve_payment(self, request, queryset):
        count = 0
        for payment in queryset:
            # Only process if not already processed OR if user isn't premium yet
            if not payment.is_approved or not payment.user.is_premium:
                self.perform_upgrade(request, payment)
                payment.is_approved = True
                payment.save()
                count += 1
        
        self.message_user(request, f"{count} payments approved & users upgraded!")
    
    approve_payment.short_description = "✅ Approve selected payments"

    # --- SHARED UPGRADE FUNCTION ---
    def perform_upgrade(self, request, payment):
        user = payment.user
        user.is_premium = True
        
        # Calculate Expiry
        if payment.plan_type == 'yearly':
            user.subscription_expiry = date.today() + timedelta(days=365)
        else:
            # Default to monthly (30 days)
            user.subscription_expiry = date.today() + timedelta(days=30)
        
        user.save()

admin.site.register(PaymentRequest, PaymentRequestAdmin)