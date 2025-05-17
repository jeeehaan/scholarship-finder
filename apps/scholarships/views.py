from django.shortcuts import render
from django.views.generic import ListView
from apps.scholarships.models import Scholarship


# Create your views here.
class ScholarshipListView(ListView):
    model = Scholarship
    template_name = "dashboard.html"
