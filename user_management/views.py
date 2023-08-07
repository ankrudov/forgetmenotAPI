from .services import delete_user, register_user, login_user, update_user
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import UserSerializer, UpdateUserSerializer


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

#LoginView logs in a user 
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        idToken = request.headers.get('Authorization').split(' ')[1]
        if not idToken:
            return Response({'error':'Authorization token not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        ok, response = login_user(idToken)
        #return error if an exception is raised, return user if everything succeded
        if not ok:
            return Response(response.get('error'), status=response.get('status'))
        return Response(response.get('user'), status=response.get('status'))
    
# UpdateUserView is allows the user to update their information
class UpdateUserView(generics.UpdateAPIView): 
    serializer_class = UpdateUserSerializer
    def put(self, request, format=None):
        idToken = request.headers.get('Authorization').split(' ')[1]
        if not idToken:
            return Response({'error':'Authorization token not found'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ok, response = update_user(serializer.validated_data, idToken)
        if not ok:
            return Response(response.get('error'), status=response.get('status'))
        return Response(response.get('user'), status=response.get('status'))

#DeleteUserView, verifies token from the firebase auth send from the frontend, soft deletes user, then sends response to client for firebase deactivate
class DeleteUserView(generics.DestroyAPIView):
    def put(self, request, format=None):
        idToken = request.headers.get('Authorization').split(' ')[1]
        if not idToken:
            return Response({'error':'Authorization token not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        ok, response = delete_user(idToken)
        if not ok:
            return Response(response.get('error'), status=response.get('status'))
        return Response(response.get('user'), status=response.get('status'))