from django.db import models
from core.models import BaseModel
from django.contrib.auth.models import User

class Conversation(BaseModel):
    role = models.CharField(max_length=255)
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    

# Create your models here.
