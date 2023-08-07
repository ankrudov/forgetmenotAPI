from rest_framework import serializers
from email_validator import validate_email, EmailNotValidError
from .models import CustomUserV2

class UserSerializer(serializers.ModelSerializer):
    #validate email, phonenumber
    def validate_email(self, value):
        if self.context['request'].method in ['POST', 'PUT']:
            try:
                validate_email(value)
            except EmailNotValidError:
                raise serializers.ValidationError("Invalid email format")

        return value
    class Meta:
        model = CustomUserV2
        fields = ['pk', 'username', 'phone_number', 'updated_on', 'failed_login_attempts', 'last_failed_login', 'is_superuser', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'password', 'is_verified']
        extra_kwargs = {
            'password':{'write_only':True},
            'is_verified':{'write_only':True}
        }

#UpdatePasswordSerializer hashes the password on update and takes in a new_password from the request
class UpdateUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ['pk', 'username', 'phone_number', 'updated_on', 'failed_login_attempts', 'last_failed_login', 'is_superuser', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_verified']
