from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class NotificationType(models.Model):
    notif_type = models.CharField(max_length=10, choices=[('app', 'App'), ('email', 'Email')], default='app')

    def __str__(self):
        return f"Notification type: {self.notif_type}"

class CustomUser(models.Model):
    plan_type = models.CharField(max_length=50)
    notif_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE, null=True)
    notif_frequency = models.CharField(
        max_length=10,
        choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('off', 'Off')],
        default='daily'
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')