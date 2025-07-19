from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from users.forms import RegisterForm, LoginForm
from .models import CustomUser
from django.contrib import messages
from django.conf import settings
import requests

# Create your views here.

def verify_payment(request):
    reference = request.GET.get('reference')
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    url = f"https://api.paystack.co/transaction/verify/{reference}"

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        res_data = response.json()
        if res_data['data']['status'] == 'success':
            # Update payment record here
            if request.user.is_authenticated:
                user = request.user
                user.profile.plan_type = 'pro'
                user.profile.save()
            return redirect("core:dashboard")
    return JsonResponse({'message': 'Payment failed'}, status=400)

def register(request):
    plan = request.GET.get("plan")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                custom_user = user.profile
                custom_user.plan_type = 'pro' if plan == 'pro' else 'free'
                custom_user.save()
            except CustomUser.DoesNotExist:
                CustomUser.objects.create(
                    user=user,
                    plan_type='pro' if plan == 'pro' else 'free'
                )
            login(request, user)
            if plan == 'pro':
                return redirect("core:payment_page")
            return redirect("core:dashboard")
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