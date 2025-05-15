from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class LoginView(View):
    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")

        return redirect("login")


class RegisterView(View):
    def get(self, request):
        return render(request, "register.html")

    def post(self, request):
        # Get form data
        username = request.POST.get("username")
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Validation
        errors = {}
        if password1 != password2:
            errors["password"] = "Passwords don't match"

        if User.objects.filter(username=username).exists():
            errors["username"] = "Username already exists"

        if User.objects.filter(email=email).exists():
            errors["email"] = "Email already in use"

        if errors:
            return render(request, "register.html", {"errors": errors})

        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
            )
            login(request, user)
            return redirect("/")  # Redirect to home after registration

        except ValidationError as e:
            return render(request, "register.html", {"error": str(e)})


def logout_view(request):
    logout(request)

    return redirect("login")