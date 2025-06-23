from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tasks/', views.tasks, name='tasks'),
    path('settings/', views.settings, name='settings'),
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('mark_complete/<int:task_id>/', views.mark_complete, name='mark_complete'),
    path('ai_command/', views.ai_command, name='ai_command')
]