from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from .tasks import scrape_scholarships
from django.views import View
from .models import ScholarshipRecommendation
from .methods import query_search
from django.contrib.auth.mixins import LoginRequiredMixin

class ScholarshipListView(LoginRequiredMixin, ListView):
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
                {
                    "title": scholarship.title,
                    "degree": scholarship.degree,
                    "country": scholarship.country,
                    "type": scholarship.type,
                    "deadline": scholarship.deadline
                }
            )
        context["scholarships"] = result
        return context

    # def get(self, request, *args, **kwargs):
    #     user = self.request.user
    #     scholarship_recommendations = ScholarshipRecommendation.objects.filter(
    #         user=user
    #     )
    #     return JsonResponse(
    #         {
    #             "scholarship_recommendations": [
    #                 {
    #                     "title": scholarship.scholarship.title,
    #                     "degree": scholarship.scholarship.degree,
    #                     "country": scholarship.scholarship.country,
    #                     "type": scholarship.scholarship.type,
    #                 }
    #                 for scholarship in scholarship_recommendations
    #             ]
    #         }
    #     )


class TriggerScrapeTaskView(View):
    def get(self, request, *args, **kwargs):
        scrape_scholarships()
        return JsonResponse({"status": "Scholarship fetch task triggered"})


class TestQueryView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get("query")
        results = query_search(query)
        return JsonResponse({"results": results})
