from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from .views import index_view

from .consumer import ChatConsumer

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index_view, name="index"),
    path("", include("apps.scholarships.urls")),
    path("", include("apps.authentication.urls")),
]

websocket_urlpatterns = [
    path("ws/chat/", ChatConsumer.as_asgi()),
]

if settings.DEBUG:
  urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)