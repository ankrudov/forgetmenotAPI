from rest_framework import status
def validate_user_firebase_token(token):
    if not token:
        return False, {'error':'invalid token', 'status':status.HTTP_400_BAD_REQUEST}
    return True,''