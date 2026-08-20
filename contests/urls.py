from django.urls import path
from . import views

app_name = 'contests'

urlpatterns = [
    path(
        '',
        views.contests_showcase,
        name='showcase'
    ),
    path(
    'vote/<int:submission_id>/',
    views.vote,
    name='vote'
),
]