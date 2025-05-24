from django.views.generic import DetailView, TemplateView
from django.http import JsonResponse
from .tasks import scrape_scholarships
from django.views import View
from .models import ScholarshipRecommendation, Scholarship
from .methods import query_search
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.chat.models import Conversation

class ScholarshipListView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        scholarship_recommendations = ScholarshipRecommendation.objects.filter(
            user=user
        )
        
        result = []
        for recommendation in scholarship_recommendations:
            scholarship = recommendation.scholarship
            result.append(
                {   "id": scholarship.id,
                    "title": scholarship.title,
                    "degree": scholarship.degree,
                    "country": scholarship.country,
                    "type": scholarship.type,
                    "deadline": scholarship.deadline
                }
            )
        context["scholarships"] = result
        conversation = Conversation.objects.filter(user=user).order_by('created_at')
        context['conversation'] = conversation
        return context


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

class ScholarshipSemanticSearchView(TemplateView):
    template_name = "search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "")

        if query:
            search_results = query_search(query)
        else:
            search_results = []

        context["scholarships"] = search_results
        context["query"] = query
        return context