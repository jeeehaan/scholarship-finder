from django.urls import path
from .views import ScholarshipListView, TriggerScrapeTaskView

urlpatterns = [
    path("dashboard/", ScholarshipListView.as_view(), name="scholarship-list"),
    path("scrape/", TriggerScrapeTaskView.as_view(), name="trigger-scrape")
]
