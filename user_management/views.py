from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from .models import CustomUser
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import UserSerializer
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from datetime import timedelta

# Create your views here.
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        #validate the serializer, checking if valid
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        #attempt to save user to DB
        try:
            user = serializer.save()
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
        
        response_data = {
            'message':f'User: {user.username} created succesfully, Please check your email for verification.'
        }

        return Response(response_data, status=status.HTTP_201_CREATED)     

#LoginView logs in a user and returns a JWT token
class LoginView(TokenObtainPairView):
    serializer_class = JSONWebTokenSerializer
    
    def post(self, request, *args, **kwargs):
        ##Get username and password from the request
        username = request.data.get('username')
        password = request.data.get('password')

        ##Check if the user exists
        try:
            user = CustomUser.objects.get(username = username)
        except ObjectDoesNotExist:
            return Response({'error': 'Username does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        
        #check if the user is locked out from failed attempts 
        lockout_threshold = 8
        lockout_duration = 5
        #check if the user has had the max amount of login attempts and their last failed login is less than 5 minutes 
        if user.failed_login_attempts >= lockout_threshold and timezone.now() < user.last_failed_login + timedelta(minutes=lockout_duration):
            return Response({'error':'Account locked due to multiple failed attempts. Try again later'},status=status.HTTP_403_FORBIDDEN)
        
        #checking the users password
        if not user.check_password(password):
            #if the password is wrong, increment the amount of failed attempts
            user.failed_login_attempts += 1
            user.last_failed_login = timezone.now()
            user.save()
            #If the failed attempts are above the threshold, lock the account
            if user.failed_login_attempts >= lockout_threshold:
                return Response({'error':'Account locked due to multiple failed login attempts. Try again later'},status=status.HTTP_403_FORBIDDEN)
            
            return Response({'error':'Wrong password'},status=status.HTTP_400_BAD_REQUEST)
        
        #if the passwords correct but the account was previously locked, reset attempts
        if user.failed_login_attempts >= lockout_threshold and timezone.now() >= user.last_failed_login + timedelta(minutes=lockout_duration):
            user.failed_login_attempts = 0
            user.save()

        #continue with the regular login flow
        return super().post(request, *args, **kwargs)