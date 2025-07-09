import json
import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .mcp import ai_response
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from .models import Task, Category, Notifications
from .memory import load_memory, save_memory, is_task_query, is_prompt_query, get_last_task, get_last_prompts
from datetime import date, datetime
from django.utils.timezone import now
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncDay
from django.db.models import Count


# Create your views here.
FALLBACK_JSON = {
    "command": "none",
    "message": "Sorry, I can't help with that 😅 I'm TaskVO — your friendly productivity assistant! Try saying something like: 'Remind me to do my homework tomorrow 🧠'"
}


def generate_description(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            task_title = data.get("title")
            if not task_title:
                return JsonResponse({"error": "No title provided."}, status=400)
            response = ai_response(f"Generate a catchy-long message for this task title: {task_title} NOTE: GO STRAIGHT TO THE POINT NO GREETINGS JUST POUR OUT THE DESCRIPTION, USE JSON {{'description'}}")
            print(type(response))

            # If ai_response returns a JSON string, parse it
            if isinstance(response, str):
                try:
                    response_json = json.loads(response)
                    if "description" in response_json:
                        return JsonResponse({"description": response_json["description"]})
                except Exception:
                    # If not a JSON string, just return as is
                    return JsonResponse({"description": response})
            elif isinstance(response, dict) and "description" in response:
                return JsonResponse({"description": response["description"]})
            return JsonResponse({"description": str(response)})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method."}, status=405)


def clean_ai_json(raw_response):
    # print(raw_response)
    try:
        raw_response = raw_response.strip()
        if not raw_response.startswith('{') or not raw_response.endswith('}'):
            print(f"[⚠️ CLEANING ERROR]: Non-JSON text detected: {raw_response}")
            return FALLBACK_JSON
        parsed = json.loads(raw_response)
        if "command" not in parsed or (parsed["command"] == "add" and "title" not in parsed):
            print(f"[⚠️ CLEANING ERROR]: Invalid JSON structure: {raw_response}")
            return FALLBACK_JSON
        return parsed
    except Exception as e:
        print(f"[⚠️ CLEANING ERROR]: {raw_response}, {e}")
        return FALLBACK_JSON

@login_required(login_url='users:login')
def ai_command(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get('user_message')
        user_id = str(request.user.id)
        history = load_memory(user_id, max_messages=2)

        # Handle prompt queries directly for efficiency
        if is_prompt_query(user_message):
            count = "all" if "all" in user_message.lower() or "chat history" in user_message.lower() else 3 if "last 3 prompts" in user_message.lower() else 1
            prompts = get_last_prompts(user_id, count=count)
            if prompts:
                message = f"Your last {count if count != 'all' else ''} prompt{'s were' if count != 1 else ' was'}:\n" + "\n".join(f"{i+1}. {p}" for i, p in enumerate(prompts)) if count != 1 else prompts[0]
                return JsonResponse({"message": message})
            return JsonResponse({"message": "No previous prompts found."})

        # Handle task queries directly
        if is_task_query(user_message):
            tasks = get_last_task(user_id, count=1)
            if tasks:
                title, due = tasks[0]
                last_task = Task.objects.filter(user=request.user).order_by('-created_at').first()
                if last_task and (not title or last_task.title != title):
                    title, due = last_task.title, "today" if last_task.due_date.date() == timezone.now().date() else "tomorrow"
                return JsonResponse({"message": f"The last task you added was: {title} (due {due})"})
            return JsonResponse({"message": "You haven't added any tasks yet."})

        # Initial AI call
        needs_context = user_message.lower() in ["delete that task", "complete that task", "do that"]
        is_specific_command = any(kw in user_message.lower() for kw in ["delete", "complete"]) and len(user_message.split()) > 3

        context = ""
        if needs_context and not is_specific_command:
            context = "\n".join([f"{m['role'].capitalize()}: {m['message']}" for m in history])
        prompt = f"Respond to this user message with a valid JSON object as per TaskVO rules: {user_message}\n{context}"

        raw_response = ai_response(prompt)
        print(raw_response)
        ai_data = clean_ai_json(raw_response)
        # print(ai_data)
        save_memory(user_id, user_message, raw_response)

        # Handle fetch_history command
        if ai_data.get("command") == "fetch_history":
            history_type = ai_data.get("type")
            count = ai_data.get("count", 1)
            if history_type == "prompt":
                prompts = get_last_prompts(user_id, count=count)
                if prompts:
                    history_text = "\n".join(f"{i+1}. {p}" for i, p in enumerate(prompts)) if count != "all" and count > 1 else prompts[0] if prompts else "No previous prompts found."
                    # Re-call AI to format response
                    prompt = f"Format this history into a JSON response as per TaskVO rules: {history_text}"
                    raw_response = ai_response(prompt)
                    ai_data = clean_ai_json(raw_response)
                    save_memory(user_id, user_message, raw_response)
                    return JsonResponse({"message": ai_data.get("message", "Error formatting history.")})
                return JsonResponse({"message": "No previous prompts found."})
            elif history_type == "task":
                tasks = get_last_task(user_id, count=count)
                if tasks:
                    history_text = "\n".join(f"{i+1}. {title} (due {due})" for i, (title, due) in enumerate(tasks))
                    prompt = f"Format this task history into a JSON response as per TaskVO rules: {history_text}"
                    raw_response = ai_response(prompt)
                    ai_data = clean_ai_json(raw_response)
                    save_memory(user_id, user_message, raw_response)
                    return JsonResponse({"message": ai_data.get("message", "Error formatting task history.")})
                return JsonResponse({"message": "You haven't added any tasks yet."})

        # Handle other commands
        command = ai_data.get("command")
        title = ai_data.get("title")
        message = ai_data.get("message")
        due = ai_data.get("due")
        task_id = ai_data.get("id")

        if command == "none" and message:
            return JsonResponse({'message': f'{message}'})
        elif command == "add-multiple":
            tasks = ai_data.get("tasks", [])
            if len(tasks) > 50:
                return JsonResponse({"message": "Woahh slow down! I can only handle 50 tasks at a time 😅"})
            for task in tasks:
                title = task.get("title")
                due = task.get("due", "today")
                if title:
                    due_date = timezone.now()
                    if due == "tomorrow":
                        due_date += timedelta(days=1)
                    elif due == "yesterday":
                        due_date -= timedelta(days=1)
                    
                    Task.objects.create(user=request.user, title=title, due_date=due_date)
            return JsonResponse({"message": f"{len(tasks)} task(s) added!"})
        elif command == "add" and title:
            description = ai_data.get("description")
            category_name = ai_data.get("category")
            due_date = timezone.now()
            if due == "tomorrow":
                due_date += timedelta(days=1)
            elif due == "yesterday":
                due_date -= timedelta(days=1)
                
            category = Category.objects.create(
                user=request.user,
                name=category_name,
                is_others=False if category_name != "Other" else True
            )
            Task.objects.create(user=request.user, title=title, description=description, category=category, due_date=due_date)
            return JsonResponse({'message': f'Task "{title}" added for {due}'})
        elif command == "delete":
            if task_id:
                try:
                    task = Task.objects.get(id=task_id, user=request.user)
                    task.delete()
                    return JsonResponse({"message": f"Task #{task_id} deleted!"})
                except:
                    return JsonResponse({"message": f"Task #{task_id} not found!"})
            elif title:
                matches = Task.objects.filter(title__icontains=title, user=request.user)[:10]
                if not matches:
                    return JsonResponse({"message": f"No tasks found with the name '{title}' 😅"})
                elif matches.count() == 1:
                    deleted_title = matches[0].title
                    matches[0].delete()
                    return JsonResponse({"message": f"✅ Task '{deleted_title}' deleted automatically!"})
                response_list = [f"#{t.id}: {t.title} ({t.due_date.date()})" for t in matches]
                message = "I found multiple tasks with that name:\n" + "\n".join(response_list) + "\nTell me which ID to delete!"
                return JsonResponse({"message": message})
            else:
                return JsonResponse({"message": "Which task to delete? Specify title or ID."})
        elif command == "complete":
            if task_id:
                try:
                    task = Task.objects.get(id=task_id, user=request.user)
                    task.completed = True
                    task.save()
                    return JsonResponse({"message": f"Task #{task_id} marked complete!"})
                except:
                    return JsonResponse({"message": f"Task #{task_id} not found!"})
            elif title:
                matches = Task.objects.filter(title__icontains=title, user=request.user)[:10]
                print(matches)
                if not matches:
                    return JsonResponse({"message": f"No tasks found with the name '{title}' 😅"})
                elif matches.count() == 1:
                    task = Task.objects.get(title__icontains=title, user=request.user)
                    task.completed = True
                    task.save()
                    return JsonResponse({"message": f"✅ Task '{task.title}' marked as complete!"})
                response_list = [f"#{t.id}: {t.title} ({t.due_date.date()})" for t in matches]
                message = "I found multiple tasks with that name:\n" + "\n".join(response_list) + "\nTell me which ID to complete!"
                return JsonResponse({"message": message})
            else:
                return JsonResponse({"message": "Which task to complete? Specify title or ID."})
        else:
            return JsonResponse({"message": "That wasn't a task. Try asking me to add something!"})
    return JsonResponse({'message': 'Invalid request method'})

    

def home(request):
    return render(request, "core/index.html")

def ai_center(request):
    return render(request, "tasks/ai.html")



@login_required(login_url='users:login')
def weekly_chart(request):
    today = now().date()
    monday = today - timedelta(days=today.weekday())  # Go back to this week's Monday

    # Filter completed tasks for current week, truncate to day
    week_data = Task.objects.filter(
        user=request.user,
        completed=True,
        created_at__date__gte=monday,
        created_at__date__lte=today
    ).annotate(
        day=TruncDay('created_at')
    ).values('day').annotate(
        count=Count('id')
    )

    # Build a full week dict with 0s (to handle missing days)
    daily_counts = { (monday + timedelta(days=i)).strftime("%a"): 0 for i in range(7) }

    for entry in week_data:
        day_name = entry['day'].strftime("%a")  # 'Mon', 'Tue', etc
        daily_counts[day_name] = entry['count']

    chart_data = {
        "labels": list(daily_counts.keys()),   # ['Mon', 'Tue', ..., 'Sun']
        "data": list(daily_counts.values())    # [3, 0, 4, 1, 0, 2, 1]
    }

    return JsonResponse(chart_data)

@login_required(login_url='users:login')
def dashboard(request):
    user = request.user
    today = today = date.today()
    tasks_left_today = Task.objects.filter(user=user, completed=False).filter(due_date__date=today).count()
    
        
    # Progress bar, for today's tasks
    # Logic: Tasks completed today / Tasks due today
    today_completed_tasks = Task.objects.filter(user=user, completed=True).filter(created_at__date=today).count()
    todays_tasks = Task.objects.filter(user=user).filter(created_at__date=today).count()
    
    progress = (today_completed_tasks / todays_tasks) * 100 if todays_tasks > 0 else 0
    
    try:
        response = requests.get('https://zenquotes.io/api/random')
        quote_data = response.json()[0]  # It's a list with one quote dict
        quote = f'"{quote_data["q"]}" - {quote_data["a"]}'
    except Exception as e:
        quote = '"You are your only limit." - Unknown'  # fallback quote

    # Do your usual task fetching here
    context = {
        "user": request.user,
        "tasks_left_today": tasks_left_today,  # your actual logic
        "progress": progress,          # your progress logic
        "today_completed_tasks": today_completed_tasks,
        "todays_tasks": todays_tasks,
        "daily_quote": quote
    }
    return render(request, "tasks/dashboard.html", context)


@login_required(login_url='users:login')
def tasks(request):
    category_name = request.POST.get("category_filter")

    is_completed_or_pending = request.GET.get("filter")
    query = request.GET.get("q")
    
    if is_completed_or_pending == "completed":
        all_tasks = Task.objects.filter(completed=True).filter(user=request.user)
    elif is_completed_or_pending == "pending":
        all_tasks = Task.objects.filter(completed=False).filter(user=request.user)
    else:
        all_tasks = Task.objects.filter(user=request.user)
    
    if query:
        all_tasks = Task.objects.filter(title__icontains=query).filter(user=request.user)
        
        

    if request.method == "POST":
        # Category dropdown filter(check if category name is not all, then filter by the category_name)
        if category_name == "all":
            all_tasks = Task.objects.filter(user=request.user)
        else:
            all_tasks = Task.objects.filter(category__name=category_name).filter(user=request.user)
    
        # Save logic
        title = request.POST.get("task_text")
        description = request.POST.get("task_description")
        category = request.POST.get("task_category")
        task_other_category = request.POST.get("other_category_text")
        due_date = request.POST.get("due_date")
        
        if all([title, category]):
            category = Category.objects.create(
                user=request.user,
                name=category if category != "Other" else task_other_category,
                is_others = False if category != "Other" else True,
            )
        
            new_task = Task.objects.create(
                title=title,
                category=category,
                description=description,
                due_date=due_date,
                user=request.user,
            )
            
            category.save()
            new_task.save()
            
            return redirect("core:dashboard")
        else:
            print("Field missing or something went wrong!")
    
    # Task display and category logic
    is_others_category = Category.objects.filter(is_others=True).filter(user=request.user)
    duplicates_removed = list({cat.name: cat for cat in is_others_category}.values())

    return render(request, "tasks/tasks.html", {"all_tasks": all_tasks, "duplicates_removed": duplicates_removed, "category_name": category_name})

@login_required(login_url='users:login')
def mark_complete(request, task_id):
    if request.method == "POST":
        task = Task.objects.get(id=task_id)
        task.completed = True
        task.save()
    
    return redirect("core:tasks")


@login_required(login_url='users:login')
def edit_task(request, task_id):
    task = Task.objects.get(id=task_id)
    data = {
        "title": task.title,
        "description": task.description,
        "due_date": task.due_date.strftime('%Y-%m-%d')
    }
    return JsonResponse(data, safe=False)

@login_required(login_url='users:login')
def delete_task(request, task_id):
    task = Task.objects.get(id=task_id)
    if request.method == "POST":
        task.delete()
        return redirect("core:tasks")


@login_required(login_url='users:login')
def get_notifications(request):
    user = request.user
    notifications = Notifications.objects.filter(user=user).order_by("-timestamp")
    data = [{
        "id": n.id,
        "type": n.type,
        "message": n.message,
        "timestamp": n.timestamp.isoformat(),
        "read": n.read
    } for n in notifications]
    return JsonResponse(data, safe=False)

def mark_read(request, notification_id):
    Notifications.objects.filter(user=request.user, id=notification_id).update(read=True)
    return JsonResponse({"status": "ok"})

def delete_notification(request, notification_id):
    Notifications.objects.filter(user=request.user, id=notification_id).delete()
    return JsonResponse({"status": "deleted"})

@login_required(login_url='users:login')
def notification(request):
    notifications = Notifications.objects.filter(user=request.user)
    return render(request, "tasks/notifications.html", {"notifications": notifications})

@login_required(login_url='users:login')
def calendar(request):
    # Filter tasks for the currently logged-in user
    # and exclude tasks where due_date is None
    tasks = Task.objects.filter(user=request.user).exclude(due_date=None)
    event_list = []
    for task in tasks:
        # Ensure category name is sent, or None if category is not set
        category_name = task.category.name if task.category else None
        
        event_list.append({
            "id": task.id,
            "title": task.title,
            "start": task.due_date.isoformat(), # This correctly converts DateTimeField to ISO string
            "description": task.description,
            "category": category_name, # Send the category name, which can be None
            "completed": task.completed
        })
    return JsonResponse(event_list, safe=False)

@login_required(login_url='users:login')    
def calendar_page(request):
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))

    # 👇 This creates a datetime object just for the first of that month
    display_date = datetime(year, month, 1)

    context = {
        'display_date': display_date,
        'prev_month': (month - 1) if month > 1 else 12,
        'prev_year': year if month > 1 else year - 1,
        'next_month': (month + 1) if month < 12 else 1,
        'next_year': year if month < 12 else year + 1,
    }
    return render(request, "tasks/calendar.html", context)

@login_required(login_url='users:login')
def settings(request):
    user = request.user
    # Profile edit
    
    username = request.POST.get("name")
    email = request.POST.get("email")
    current_password = request.POST.get("current-password")
    new_password = request.POST.get("new-password")
    confirm_password = request.POST.get("confirm-password")
    
    if request.method == "POST":
        if new_password:
            if new_password == confirm_password and check_password(current_password, user.password):
                user.set_password(new_password)
                user.save()
                return redirect("core:dashboard")
            else:
                return redirect("core:settings")
        else:
            user.username = username
            user.email = email
            user.save()
            return redirect("core:dashboard")
    return render(request, "tasks/settings.html")