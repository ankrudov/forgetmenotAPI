from django.db import models
from django.contrib.auth.models import AbstractUser

# the user model is a table in charge of holding user information for user management
class CustomUserV2(AbstractUser): 
    phone_number = models.CharField(max_length=100)
    updated_on = models.DateTimeField(auto_now=True)
    failed_login_attempts = models.IntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True)

    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'users_V2'
