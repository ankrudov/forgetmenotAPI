from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=50)
    first_name= models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    password = models.CharField(max_length=200)
    email = models.EmailField(max_length=100)
    phone_number = models.CharField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=50)
    deleted = models.BooleanField(default=False)

    #ENUMS to later be used to check if an account is banned,active, or inactive and 
    ACCOUNT_STATUS_ENUMS = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('banned', 'Banned')
    )

    account_status = models.CharField(max_length=15,choices=ACCOUNT_STATUS_ENUMS)

    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'users'