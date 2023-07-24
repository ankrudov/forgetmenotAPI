from .models import CustomUserV2
from firebase_admin import auth
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist



#check_password takes in a user object, and a password,returns a boolean 
def verify_password(user, password):
    if not user.check_password(password):
        return False
    else:
        return True

#delete_user deletes a user
def delete_user(user):
    try:
        user.delete()
        return True, {"success": "user deleted"}
    except ObjectDoesNotExist:
        return False, {"error": "object does not exist"}
    
def register_user(validated_data):
    # Get user data from the validated data
    username = validated_data.get('username')
    first_name = validated_data.get('first_name')
    last_name = validated_data.get('last_name')
    is_superuser = validated_data.get('is_superuser')
    is_staff = validated_data.get('is_staff')
    is_active = validated_data.get('is_active')
    phone_number = validated_data.get('phone_number')
    email = validated_data.get('email')
    password = validated_data.get('password')

    #create user in firebase authentication
    try:
        user = auth.create_user(email=email, password=password)
    except Exception as e:
        return {'message': str(e), 'status':status.HTTP_400_BAD_REQUEST}
    
    #save user to DB 
    user_model = CustomUserV2.objects.create(
        username=username,
        first_name=first_name,
        last_name=last_name,
        is_superuser=is_superuser,
        is_staff=is_staff,
        is_active=is_active,
        phone_number=phone_number,
    )
    response_data = {
        'message': f'User: {user_model.username} created successfully. Please check your email for verification.',
        'status': status.HTTP_201_CREATED
    }
    return response_data