from django.contrib import admin
from .models import Scholarship

# Register your models here.


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
        "degree",
        "deadline",
        "registration_start_date",
        "country",
        "type",
        "created_at",
        "official_url",
        "source_url",
        "benefits",
        "requirements",
    )