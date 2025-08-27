# users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import CustomUser

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Default every new user to free unless changed later
        CustomUser.objects.create(user=instance, plan_type="free")
    else:
        # Keep profile in sync
        if hasattr(instance, "profile"):
            instance.profile.save()
