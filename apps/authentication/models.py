from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel

class Profile(BaseModel):
    # One-to-one link with Django User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Basic Info
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Academic Info
    education_level = models.CharField(max_length=50, blank=True, null=True)
    field_of_study = models.CharField(max_length=100, blank=True, null=True)
    gpa = models.FloatField(blank=True, null=True)
    target_degree = models.CharField(max_length=50, blank=True, null=True)
    sat_score = models.PositiveIntegerField(blank=True, null=True)
    act_score = models.PositiveIntegerField(blank=True, null=True)
    gre_score = models.PositiveIntegerField(blank=True, null=True)
    other_test = models.CharField(max_length=100, blank=True, null=True)
    institution = models.CharField(max_length=200, blank=True, null=True)
    
    # Demographic Info
    date_of_birth = models.DateField(blank=True, null=True)    
    gender = models.CharField(max_length=20, blank=True, null=True)
    ethnicity = models.CharField(max_length=100, blank=True, null=True)    
    citizenship = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    
    # Financial & Background
    income_bracket = models.CharField(max_length=100, blank=True, null=True)
    first_generation = models.BooleanField(default=False, blank=True, null=True)
    has_disability = models.BooleanField(default=False, blank=True, null=True)
    military_affiliation = models.BooleanField(default=False, blank=True, null=True)
    special_circumstances = models.TextField(blank=True, null=True)
    
    # Interests & Goals
    career_goals = models.TextField(blank=True, null=True)
    extracurricular_activities = models.JSONField(default=list, blank=True, null=True, help_text="User preferences in JSON format")
    volunteer_experience = models.TextField(blank=True, null=True)
    special_talents = models.CharField(max_length=200, blank=True, null=True)
    
    # Preferences
    preferred_location = models.JSONField(default=list, blank=True, null=True, help_text="User preferred study locatoin in JSON format")
    study_format = models.CharField(max_length=100, blank=True, null=True)    
    willing_to_relocate = models.CharField(max_length=100, blank=True, null=True)    
    scholarship_types = models.JSONField(default=list, blank=True, null=True, help_text="Multiple scholarship types selected by users")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s Profile (Created: {self.created_at})"