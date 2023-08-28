from django.db import models
from user_management.models import CustomUserV2
from django.utils import timezone

class Contact(models.Model):
    user = models.ForeignKey(CustomUserV2, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=150)
    created_on = models.DateTimeField(("created on"), default=timezone.now)
    updated_on = models.DateTimeField(auto_now=True)