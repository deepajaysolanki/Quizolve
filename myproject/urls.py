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

    # site wise pages
  #  path('', include('myapp.urls')), 
    path('', views.home_page, name='home-page'),  
    path('about/', views.about_page, name='about-page'),  
    path('quiz/', views.quiz_page, name='quiz-page'),  
    path('contact/', views.contact_page, name='contact-page'),  

    # user authentication pages
    path('login/', views.login_form, name='login'),
    path('registration/', views.registration_form, name='registration'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='user-profile'),
    path('profile/edit/', views.profile_edit_view, name='profile-edit'),

    # quiz app URLs
    path('quiz/', include('myapp.urls')),

    # Include for allauth and password reset
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('accounts/3rdparty/login/cancelled/', RedirectView.as_view(url=reverse_lazy('login')), name='socialaccount_login_cancelled'),
    path('accounts/password/change/', allauth_views.PasswordChangeView.as_view(template_name='user/password_change_form.html', form_class=CustomPasswordChangeForm, success_url=reverse_lazy('user-profile')), name='account_password_change'),
    path('accounts/', include('allauth.urls')), # for signup with google gunctionality

     # Exam quiz URLs
    path('exams/', views.exam_selection_view, name='exam-selection'),
    path('exams/start/<str:exam_name>/', views.start_exam_quiz_view, name='start-exam-quiz'),
    # Note: We can reuse the existing play_quiz page, just give it a new URL name
    path('exams/play/', views.play_quiz_view, name='play-exam-quiz'),
    path('api/end-exam-early/', views.end_exam_quiz_early_api, name='end-exam-early')
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)