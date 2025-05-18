from django.contrib import admin
from django.urls import include, path

from .views import index_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index_view, name="index"),
    path("", include("apps.scholarships.urls")),
    path("", include("apps.authentication.urls")),
]
