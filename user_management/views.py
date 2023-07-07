from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import UserSerializer
# from rest_framework_jwt.serializers import JSONWebTokenSerializer
# from rest_framework_jwt.views import ObtainJSONWebToken

# Create your views here.
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def register_user(self, request, *args, **kwargs):
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
