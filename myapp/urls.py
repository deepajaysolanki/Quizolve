from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.contrib.sites.models import Site
from django.http import HttpResponse

# 1. Create the temporary function
def fix_site_error(request):
    Site.objects.update_or_create(
        id=1, 
        defaults={'domain': 'quizolve.onrender.com', 'name': 'Quizolve'}
    )
    return HttpResponse("Site ID 1 created successfully! You can delete this code now.")

urlpatterns = [
    path('', views.quiz_page, name='quiz-page'),

     # Quiz Page URLs
    path('start/', views.start_quiz_view, name='start-quiz'),
    path('play/', views.play_quiz_view, name='play-quiz'),
    path('results/', views.results_view, name='results-page'),

    # API URLs for JavaScript
    path('api/get-question/', views.get_next_question_api, name='api-get-question'),
    path('api/check-answer/', views.check_answer_api, name='api-check-answer'),

    # User Authentication URLs
    path('fix-site/', fix_site_error),
]
