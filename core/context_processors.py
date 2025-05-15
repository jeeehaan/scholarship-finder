import time

from django.conf import settings


def cache_buster(request):
    return {"CACHE_BUSTER": str(int(time.time())) if settings.DEBUG else ""}
