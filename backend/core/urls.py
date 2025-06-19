from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tasks/', views.tasks, name='tasks'),
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('filtered_tasks/', views.filtered_tasks, name='filtered_tasks'),
]