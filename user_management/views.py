from datetime import timedelta

from .models import CustomUserV2
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import UserSerializer, UpdatePasswordSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated

# CreateUserView creates a user
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request):
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
    #specify the serializer class that the view will use for validating and parsing the incoming data and for serializing the outgoing data.
    serializer_class = TokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        ##Get username and password from the request
        username = request.data.get('username')
        password = request.data.get('password')

        ##Check if the user exists
        try:
            user = CustomUserV2.objects.get(username = username)
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
        token_response = super().post(request, *args, **kwargs)
        token = token_response.data
        user_serializer = UserSerializer(user)
        
        #return the response with the user data, refresh token and access token
        return Response({
            'user': user_serializer.data,
            'access_token': token.get('access'),
            'refresh_token':token.get('refresh')
        }, status=200)
    
# UpdateUserView is allows the user to update their information
class UpdateUserView(generics.UpdateAPIView): 
    #make sure user is authenticated before allowing access
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return CustomUserV2.objects.get(pk=pk)
        except CustomUserV2.DoesNotExist:
            return Response({'error':'User does not exist'},status=status.HTTP_404_NOT_FOUND)
        
    def put(self, request, pk, format=None):
        #get user object from the db
        user = self.get_object(pk)
        #if the user requesting to update isnt the same as the user from the db, send denied
        if not request.user == user:
            return Response({'denied:':'Access Denied'},status=status.HTTP_403_FORBIDDEN)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#UpdatePasswordView checks a users old password match, and updates with new password
class UpdatePasswordView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        #get old password
        old_password = request.data.get('old_password')
        # Get the user from the authenticated request.
        user = get_object_or_404(CustomUserV2, username=request.user.username)

        ##if the old password does not match return error
        if not user.check_password(old_password):
            return Response({'error':'Password does not match'}, status=status.HTTP_403_FORBIDDEN)
        
        ##if it does match serialize the data
        serializer = UpdatePasswordSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success':'Password updated'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#DeleteUserView, verify password, if it matches delete