from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from core.models import Task, Notifications
from users.models import CustomUser

class Command(BaseCommand):
    help = 'Send notifications for due tasks (email and/or app)'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        for custom_user in CustomUser.objects.filter(notif_frequency__in=['daily', 'weekly']):
            # Check if today matches their frequency
            if custom_user.notif_frequency == 'daily' or (
                custom_user.notif_frequency == 'weekly' and now.weekday() == 0  # Monday
            ):
                notif_type = custom_user.notif_type.notif_type if custom_user.notif_type else ''
                due_tasks = Task.objects.filter(
                    user=custom_user.user,
                    due_date__lte=now,
                    completed=False,
                    is_due=False
                )
                for task in due_tasks:
                    # Send email if enabled
                    if 'email' in notif_type:
                        user_email = custom_user.user.email
                        if user_email:
                            send_mail(
                                subject='Task Due Reminder',
                                message=f'Your task "{task.title}" is due!',
                                from_email='noreply@taskvo.com',
                                recipient_list=[user_email],
                                fail_silently=False,
                            )
                    # Send app notification if enabled
                    if 'app' in notif_type:
                        Notifications.objects.create(
                            user=custom_user.user,
                            message=f'Your task "{task.title}" is due!',
                            type='reminder'
                        )
                    task.is_due = True
                    task.save()
        self.stdout.write(self.style.SUCCESS('Due task notifications sent.'))