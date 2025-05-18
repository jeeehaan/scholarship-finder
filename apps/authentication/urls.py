from django.urls import path

from apps.authentication.views import LoginView, RegisterView, logout_view, OnboardingView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("logout/", logout_view, name="logout"),
    path('onboarding/', OnboardingView.as_view(), name='onboarding'),    
]
