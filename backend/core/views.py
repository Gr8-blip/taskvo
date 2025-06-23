import json
import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .mcp import ai_response
from django.contrib.auth.decorators import login_required
from .models import Task, Category
from datetime import date

# Create your views here.

def ai_command(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get('user_message')
        raw_response = ai_response(user_message)

        try:
            # AI gave us JSON string, let’s parse it
            ai_data = json.loads(raw_response)
            print(raw_response)
            command = ai_data.get("command")
            title = ai_data.get("title")
            message = ai_data.get("message")
            due = ai_data.get("due")
            
            if command == "none" and message:
                return JsonResponse({'message': f'{message}'})

            if command == "add" and title:
                # Convert "today" to actual date
                from django.utils import timezone
                from datetime import datetime, timedelta

                if due == "today":
                    due_date = timezone.now()
                elif due == "tomorrow":
                    due_date = timezone.now() + timedelta(days=1)
                else:
                    # Try parsing ISO or fallback
                    try:
                        due_date = datetime.fromisoformat(due)
                    except:
                        due_date = timezone.now()

                # Save task
                Task.objects.create(
                    user=request.user,
                    title=title,
                    due_date=due_date
                )

                return JsonResponse({'message': f'Task "{title}" added for {due}'})
            else:
                return JsonResponse({"message": "That wasn't a task. Try asking me to add something!"})
        except Exception as e:
            print(raw_response)
            return JsonResponse({'message': f"Failed to parse AI response: {e}"})

def home(request):
    return render(request, "core/index.html")


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


def mark_complete(request, task_id):
    if request.method == "POST":
        task = Task.objects.get(id=task_id)
        task.completed = True
        task.save()
    
    return redirect("core:tasks")

def delete_task(request, task_id):
    task = Task.objects.get(id=task_id)
    if request.method == "POST":
        task.delete()
        return redirect("core:tasks")
    
def settings(request):
    return render(request, "tasks/settings.html")