from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class CustomUser(models.Model):
    plan_type = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')