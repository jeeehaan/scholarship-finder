from django.db import models
from django.contrib.postgres.fields import ArrayField

from core.models import BaseModel

DEGREE_LEVEL_CHOICES = (("bachelor", "Bachelor"), ("master", "Master"))

TYPE_CHOICES = (("full", "Full"), ("partial", "Partial"))


class Scholarship(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    degree = models.CharField(max_length=100)
    deadline = models.DateField(blank=True, null=True)
    registration_start_date = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    benefits = ArrayField(models.CharField(max_length=255))
    requirements = ArrayField(models.CharField(max_length=255))
    official_url = models.URLField(unique=True)
    source_url = models.URLField(unique=True, blank=True, null=True)
