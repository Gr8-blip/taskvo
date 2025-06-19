from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Task, Category
# Create your views here.
def home(request):
    return render(request, "core/index.html")

@login_required(login_url='users:login')
def dashboard(request):
    user = request.user
    return render(request, "tasks/dashboard.html", {"user": user})


@login_required(login_url='users:login')
def tasks(request):
    if request.method == "POST":
        title = request.POST.get("task_text")
        description = request.POST.get("task_description")
        category = request.POST.get("task_category")
        task_other_category = request.POST.get("other_category_text")
        due_date = request.POST.get("due_date")
        
        
        category = Category.objects.create(
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
    
    all_tasks = Task.objects.filter(user=request.user)
    is_others_category = Category.objects.filter(is_others=True)
    filtered_tasks_ids = request.session.pop('filtered_task_ids', None)
    filtered_tasks = Task.objects.filter(id__in=filtered_tasks_ids) if filtered_tasks_ids else None
    return render(request, "tasks/tasks.html", {"all_tasks": all_tasks, "is_others_category": is_others_category, "filtered_tasks": filtered_tasks})

def filtered_tasks(request):
    query = request.GET.get('q')
    filtered = Task.objects.filter(title__icontains=query, user=request.user)
    request.session['filtered_task_ids'] = list(filtered.values_list('id', flat=True))
    
    return HttpResponseRedirect(reverse('core:tasks'))

def delete_task(request, task_id):
    task = Task.objects.get(id=task_id)
    if request.method == "POST":
        task.delete()
        return redirect("core:tasks")