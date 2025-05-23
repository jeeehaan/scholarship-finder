from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Profile
from apps.scholarships.methods import generate_preference_query
import json


class LoginView(View):
    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/dashboard")

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
            return redirect("/onboarding")  # Redirect to home after registration

        except ValidationError as e:
            return render(request, "register.html", {"error": str(e)})


def logout_view(request):
    logout(request)

    return redirect("login")

class OnboardingView(LoginRequiredMixin, TemplateView):
    template_name = 'onboarding.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Only get basic info for the form defaults
        context['user_data'] = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        return context
    
    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.get('data', '{}'))
        
        user = request.user    
        
        # Update User model
        user.first_name = data.get('first_name', '')
        user.last_name = data.get('last_name', '')
        user.email = data.get('email', '')
        user.save()
        
        # Get or create profile ONLY when form is submitted
        profile, created = Profile.objects.get_or_create(user=user)                
        
        # Helper function to clean numeric fields
        def clean_number(value):
            if value == '' or value is None:
                return None
            try:
                return int(value) if value.isdigit() else float(value)
            except (ValueError, AttributeError):
                return None
        
        # Clean numeric fields
        numeric_fields = ['gpa', 'sat_score', 'act_score', 'gre_score']
        for field in numeric_fields:
            if field in data:
                data[field] = clean_number(data[field])
        
        # Use dictionary to map form fields to model fields
        field_mapping = {
            # Basic Info
            'phone': 'phone',
            
            # Academic Info
            'education_level': 'education_level',
            'field_of_study': 'field_of_study',
            'gpa': 'gpa',
            'target_degree': 'target_degree',
            'sat_score': 'sat_score',
            'act_score': 'act_score',
            'gre_score': 'gre_score',
            'other_test': 'other_test',
            'institution': 'institution',
            
            # Demographic Info
            'date_of_birth': 'date_of_birth',
            'gender': 'gender',
            'ethnicity': 'ethnicity',
            'citizenship': 'citizenship',
            'country': 'country',
            
            # Financial & Background
            'income_bracket': 'income_bracket',
            'first_generation': 'first_generation',
            'has_disability': 'has_disability',
            'military_affiliation': 'military_affiliation',
            'special_circumstances': 'special_circumstances',
            
            # Interests & Goals
            'career_goals': 'career_goals',
            'volunteer_experience': 'volunteer_experience',
            'special_talents': 'special_talents',
            
            # Preferences
            'preferred_location': 'preferred_location',
            'study_format': 'study_format',
            'willing_to_relocate': 'willing_to_relocate',
        }
        
        # Handle standard fields
        for form_field, model_field in field_mapping.items():
            value = data.get(form_field)
            if value is not None:
                setattr(profile, model_field, value)
        
        # Handle special cases
        profile.first_generation = 'first_generation' in data
        profile.has_disability = 'has_disability' in data
        profile.military_affiliation = 'military_affiliation' in data        
        
        # Handle array fields - they come as lists from JSON
        if 'extracurricular_activities' in data:
            profile.extracurricular_activities = data['extracurricular_activities']
        
        if 'scholarship_types' in data:
            profile.scholarship_types = data['scholarship_types']
        
        profile.save()
        
        generate_preference_query(
            user,
            profile.preferred_location,
            profile.study_format,
            profile.willing_to_relocate,
            profile.scholarship_types,
            profile.target_degree,
        )
        
        messages.success(request, 'Profile updated successfully!')
        return JsonResponse({
            'success': True,
            'redirect_url': '/'  # or reverse('profile_success')
        })