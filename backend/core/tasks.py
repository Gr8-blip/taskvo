from celery import shared_task
from django.core.management import call_command

@shared_task
def send_due_task_emails_task():
    call_command('send_due_task_emails')