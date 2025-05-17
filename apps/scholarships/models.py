from django.db import models

from core.models import BaseModel

DEGREE_LEVEL_CHOICES = (("bachelor", "Bachelor"), ("master", "Master"))

TYPE_CHOICES = (("full", "Full"), ("partial", "Partial"))


class Scholarship(BaseModel):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    degree_level = models.CharField(max_length=100, choices=DEGREE_LEVEL_CHOICES)
    end_date = models.DateField()
