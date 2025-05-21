from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from .tasks import scrape_scholarships
from django.views import View
from .models import Scholarship
from .methods import query_search

class ScholarshipListView(ListView):
    model = Scholarship
    context_object_name = "scholarships"
    ordering = ["-created_at"]
    template_name = "dashboard.html"

class ScholarshipDetailView(DetailView):
    model = Scholarship
    template_name = "scholarship-detail.html"
    context_object_name = "scholarship"
    slug_field = "id"
    slug_url_kwarg = "id"
    

class TriggerScrapeTaskView(View):
    def get(self, request, *args, **kwargs):
        scrape_scholarships()
        return JsonResponse({"status": "Scholarship fetch task triggered"})
    

class TestQueryView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get("query")
        results = query_search(query)
        return JsonResponse({"results": results})
