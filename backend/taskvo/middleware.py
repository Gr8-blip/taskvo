from django.shortcuts import redirect
from django.urls import reverse

class RedirectAuthenticationUserMiddleWare:
    def __init__(self, get_response):
        self.get_response = get_response
        self.public_urls = [
            reverse("users:login"),
            reverse("users:register"),
            reverse("core:home"),
        ]
        
    def __call__(self, request):
        user = request.user
        path = request.path
        
        if user.is_authenticated and path in self.public_urls:
            return redirect("core:dashboard")
        
        response = self.get_response(request)
        
        return response