from firebase_admin import auth
from rest_framework import authentication, exceptions
from .models import CustomUserV2

class FirebaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        header = request.META.get('HTTP_AUTHORIZATION')
        if header is None:
            return None

        _, token = header.split('Bearer ')
        decoded_token = None
        try:
            decoded_token = auth.verify_id_token(token)
        except ValueError as v:
            raise exceptions.AuthenticationFailed(str(v))
        if not decoded_token:
            return None

        return (self.get_user(decoded_token), None)

    def get_user(self, decoded_token):
        user = CustomUserV2.objects.filter(firebase_uid=decoded_token['uid']).first()
        if user is None:
            raise exceptions.AuthenticationFailed('No such user')
        return user
