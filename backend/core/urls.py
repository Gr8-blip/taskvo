from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('generate_description/', views.generate_description, name='generate_description'),
    path('ai_center/', views.ai_center, name='ai_center'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('weekly_chart/', views.weekly_chart, name='weekly_chart'),
    path('tasks/', views.tasks, name='tasks'),
    path('edit-task/<int:task_id>/', views.edit_task, name='edit_task'),
    path('notifications/', views.notification, name='notifications'),
    path('get_notifications/', views.get_notifications, name='get_notifications'),
    path('notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('notifications/mark/<int:notification_id>/', views.mark_read, name='mark_read'),
    path('settings/', views.settings, name='settings'),
    path('calendar/', views.calendar, name='calendar'),
    path('calendar_page/', views.calendar_page, name='calendar_page'),
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('mark_complete/<int:task_id>/', views.mark_complete, name='mark_complete'),
    path('ai_command/', views.ai_command, name='ai_command')
]