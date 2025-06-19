from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from users.forms import RegisterForm, LoginForm
from django.contrib import messages

# Create your views here.
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("users:login")
        else:
            print(form.errors)
            
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        username = request.POST.get("username")
        password = request.POST.get("password")
        if form.is_valid():
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect("core:dashboard")
            else:
                messages.error(request, "Invalid username or password")
    else:
        form = LoginForm()
        
    return render(request, "users/login.html", {"form": form})



def logout_view(request):
    logout(request)
    return redirect("users:login")