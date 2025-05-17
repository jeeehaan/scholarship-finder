from django.shortcuts import render
from django.views.generic import ListView
from apps.scholarships.models import Scholarship
from django.http import JsonResponse
from .tasks import scrape_scholarships
from django.views import View



# Create your views here.
class ScholarshipListView(ListView):
    model = Scholarship
    context_object_name = "scholarships"
    ordering = ["-created_at"]
    template_name = "dashboard.html"

class TriggerScrapeTaskView(View):
    def get(self, request, *args, **kwargs):
        scrape_scholarships()
        return JsonResponse({"status": "Scholarship fetch task triggered"})
