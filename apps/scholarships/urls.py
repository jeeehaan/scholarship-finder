from django.urls import path
from .views import ScholarshipListView, TriggerScrapeTaskView, TestQueryView

urlpatterns = [
    path("dashboard/", ScholarshipListView.as_view(), name="scholarship-list"),
    path("scrape/", TriggerScrapeTaskView.as_view(), name="trigger-scrape"),
    path("test-query/", TestQueryView.as_view(), name="test-query"),
]
