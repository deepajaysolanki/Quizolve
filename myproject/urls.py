from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from myapp import views
from django.contrib.auth import views as auth_views 
from django.views.generic.base import RedirectView
from django.urls import reverse_lazy
from allauth.account import views as allauth_views
from myapp.forms import CustomPasswordChangeForm

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- Site-wide Pages ---
    path('', views.home_page, name='home-page'), 
    path('about/', views.about_page, name='about-page'), 
    path('contact/', views.contact_page, name='contact-page'), 

    # --- User Authentication ---
    path('login/', views.login_view, name='login'),
    path('login/verify/', views.verify_login_otp_view, name='verify-login-otp'),
    path('registration/', views.registration_form, name='registration'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='user-profile'),
    path('profile/edit/', views.profile_edit_view, name='profile-edit'),
    path('profile/history/', views.quiz_history_view, name='quiz-history'),
    
    # FORGOT PASSWORD (OTP FLOW)
    path('forgot-password/', views.forgot_password_view, name='forgot-password'),
    path('forgot-password/verify/', views.verify_reset_otp_view, name='verify-reset-otp'),
    path('reset-password/new/', views.reset_new_password_view, name='reset-new-password'),
    
    # --- Allauth & Password Reset ---
    # These must come BEFORE the main 'accounts/' include
    path('accounts/', include('allauth.urls')),

    # --- App URLs ---
    # All regular quiz URLs are now correctly prefixed with 'quiz/'
    path('quiz/', include('myapp.urls')), 
    
    # All exam quiz URLs
    path('exams/', views.exam_selection_view, name='exam-selection'),
    path('exams/start/<str:exam_name>/', views.start_exam_quiz_view, name='start-exam-quiz'),
    path('exams/play/', views.play_quiz_view, name='play-exam-quiz'),

    # API URLs
    # These should be in app's urls.py, but for now this works.
    path('api/record-answer/', views.record_answer_api, name='record-answer-api'),
    path('api/set-ended-early/', views.set_ended_early_view, name='set-ended-early'),
    path('api/record-attempt-on-leave/', views.record_attempt_on_leave_api, name='record-attempt-on-leave'),
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)