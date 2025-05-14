from django.db import models

from core.utils import generate_id


class BaseModel(models.Model):
    id = models.CharField(
        primary_key=True, max_length=100, default=generate_id, editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
