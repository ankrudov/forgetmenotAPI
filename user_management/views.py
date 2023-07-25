from datetime import timedelta

from .models import CustomUserV2
from .services import verify_password, delete_user, register_user, login_user
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import UserSerializer, UpdatePasswordSerializer, DeleteSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from firebase_admin import auth


# CreateUserView creates a user
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request, *ars, **kwargs):
        #validate the serializer, checking if valid
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        #register the user in firebase, and save the user in db
        ok, response = register_user(serializer.validated_data)
        if not ok:
            return Response(response.get('error'), status=response.get('status'))
        return Response(response.get('response'), status=response.get('status'))

#LoginView logs in a user and returns a JWT token
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        idToken = request.META.get('HTTP_AUTHORIZATION', None)
        if idToken:
            idToken = idToken.split(' ')[1]  # Remove "Bearer " from the token string
        else:
            return Response({'error':'Authorization token not found'}, status=status.HTTP_400_BAD_REQUEST)
        ok, response = login_user(idToken)
        #return error if an exception is raised, return user if everything succeded
        if not ok:
            return Response(response.get('error'), status=response.get('status'))
        return Response(response.get('user'), status=response.get('status'))
    
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
    
#DeleteUserView, verify password and JWT token. once authenticated delete user. 
#TODO implement soft delete
class DeleteUserView(generics.DestroyAPIView):
    serializer_class = DeleteSerializer
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, format=None):
        #get password, verify its correct before deleting
        user_record = request.user
        password = request.data.get('password')
        is_password_verified = verify_password(user_record, password)

        if request.user == user_record and is_password_verified:
            ok, response = delete_user(user_record)
            if ok:
                return Response(response, status=status.HTTP_204_NO_CONTENT)
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        