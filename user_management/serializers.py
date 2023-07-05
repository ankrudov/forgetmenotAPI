from rest_framework import serializers
from email_validator import validate_email, EmailNotValidError
from .models import User

class UserSerializer(serializers.ModelSerializer):
    #validate email, phonenumber
    def validate_email(self, value):
        if self.context['request'].method in ['POST', 'PUT']:
            try:
                validate_email(value)
            except EmailNotValidError:
                raise serializers.ValidationError("Invalid email format")

        return value

    #check if username is already in use
    class Meta:
        model = User
        fields = ['pk','username', 'first_name', 'last_name', 'password', 'email', 'phone_number', 'created_on', 'updated_on', 'updated_by', 'deleted', 'account_status']