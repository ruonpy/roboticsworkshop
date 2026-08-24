from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('project/<int:project_id>/like/', views.like_project, name='like_project'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('notifications/read/', views.mark_notifications_as_read, name='mark_notifications_as_read'),
]