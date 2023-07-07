from rest_framework import serializers
from email_validator import validate_email, EmailNotValidError
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    #validate email, phonenumber
    def validate_email(self, value):
        if self.context['request'].method in ['POST', 'PUT']:
            try:
                validate_email(value)
            except EmailNotValidError:
                raise serializers.ValidationError("Invalid email format")

        return value
    #when serializer.save() is called for a POST request, hash password before saving the user instance
    def create(self, validated_data):
        password = validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    #when serializer.save() is called for a PUT or PATCH request, hash password before saving the user instance
    def update(self, instance, validated_data):
        for attr, value in validated_data:
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance,attr,value)

    class Meta:
        model = CustomUser
        fields = ['pk', 'username', 'email', 'phone_number', 'updated_on', 'failed_login_attempts', 'last_failed_login']
        extra_kwargs = {
            'password':{'write_only':True}
        }