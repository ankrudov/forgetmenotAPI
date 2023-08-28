from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import ContactSerializer
from .services import create_contact
from forgetmenotAPI.utils import validate_user_firebase_token

class CreateContactView(generics.CreateAPIView):
    serializer_class = ContactSerializer
    def post(self, request, *args, **kwargs):
        idToken = request.headers.get('Authorization').split(' ')[1]
        ok,message = validate_user_firebase_token(idToken)
        if not ok:
            return Response(message.get('error'), status=message.get('status'))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ok, response = create_contact(serializer.validated_data)
        if not ok:
            return Response(response.get('error'), status=response.get('status'))
        return Response(response.get('response'), status=response.get('status'))
