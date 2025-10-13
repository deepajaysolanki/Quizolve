from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.quiz_page, name='quiz-page'),

     # Quiz Page URLs
    path('start/', views.start_quiz_view, name='start-quiz'),
    path('play/', views.play_quiz_view, name='play-quiz'),
    path('results/', views.results_view, name='results-page'),

    # API URLs for JavaScript
    path('api/get-question/', views.get_next_question_api, name='api-get-question'),
    path('api/check-answer/', views.check_answer_api, name='api-check-answer'),
]
