import requests
from allauth.socialaccount.models import SocialToken
from django.utils.timezone import localtime, timedelta

BASE_URL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"

def get_access_token(user):
    token = SocialToken.objects.filter(account__user=user, account__provider="google").first()
    return token.token if token else None


def create_event(task, user):
    """Create a new Google Calendar event and store its ID on the Task."""
    access_token = get_access_token(user)
    if not access_token:
        return None

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    body = {
        "summary": task.title,
        "description": task.description,
        "start": {"dateTime": localtime(task.due_date).isoformat()},
        "end": {"dateTime": (task.due_date + timedelta(hours=1)).isoformat()},
    }

    resp = requests.post(BASE_URL, headers=headers, json=body)
    if resp.status_code == 200:
        event = resp.json()
        task.google_event_id = event["id"]
        task.save(update_fields=["google_event_id"])
    return resp


def update_event(task, user):
    """Update an existing Google Calendar event if google_event_id is set."""
    if not task.google_event_id:
        return None

    access_token = get_access_token(user)
    if not access_token:
        return None

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    body = {
        "summary": task.title,
        "description": task.description,
        "start": {"dateTime": localtime(task.due_date).isoformat()},
        "end": {"dateTime": (localtime(task.due_date) + task.duration()).isoformat()},
    }

    url = f"{BASE_URL}/{task.google_event_id}"
    resp = requests.patch(url, headers=headers, json=body)
    return resp


def delete_event(task, user):
    """Delete Google Calendar event if google_event_id exists."""
    if not task.google_event_id:
        return None

    access_token = get_access_token(user)
    if not access_token:
        return None

    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{BASE_URL}/{task.google_event_id}"

    resp = requests.delete(url, headers=headers)
    return resp
