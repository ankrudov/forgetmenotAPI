import os
from .models import CustomUserV2
from firebase_admin import auth
import sendgrid
from sendgrid.helpers.mail import Mail
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from .serializers import UserSerializer

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
        return False,{'error': str(e), 'status':status.HTTP_400_BAD_REQUEST}
    #get uid to store in db
    firebase_uid = user.uid
    #verification link
    verification_link = auth.generate_email_verification_link(email)
    
    #save user to DB 
    user_model = CustomUserV2.objects.create(
        username=username,
        first_name=first_name,
        last_name=last_name,
        is_superuser=is_superuser,
        is_staff=is_staff,
        is_active=is_active,
        phone_number=phone_number,
        firebase_uid = firebase_uid
    )
    try:
        send_registration_email(email, username, verification_link)
    except Exception as e:
        return False,{'error': f'Failed to send registration email: {str(e)}', 'status':status.HTTP_500_INTERNAL_SERVER_ERROR}
    try:
        user = CustomUserV2.objects.get(username=username)
        user_serializer = UserSerializer(user)
    except ObjectDoesNotExist as e:
        return False, {'error':'user not found', 'status':status.HTTP_404_NOT_FOUND}
    response_data = {
        'response':{
            'message': f'User: {user_model.username} created successfully. Please check your email for verification.',
            'user': user_serializer.data
        },
        'status': status.HTTP_201_CREATED
        
    }
    return True, response_data
#send_registration_email sends email via sendgrid
def send_registration_email(email, username, email_link):
    try:
        sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_KEY'))
        mail = Mail(
            from_email=os.environ.get("DEFAULT_FROM_EMAIL"),
            to_emails=email
        )
        mail.template_id = os.environ.get('SENDGRID_TEMPLATE_ID')
        mail.dynamic_template_data = {
            'username':username,
            'verification_link':email_link
        }
        response = sg.send(mail)
    except Exception as e:
        print(f"Error occurred while sending email: {e}")

#login_user logs in a user after verifying firebase token
def login_user(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        firebase_uid = decoded_token['uid']
        user = CustomUserV2.objects.get(firebase_uid=firebase_uid)
        user_serializer = UserSerializer(user)

        return True, {'user':user_serializer.data, 'status':status.HTTP_200_OK}
    except user.is_active == False:
        return False, {'error':'user is not active', 'status':status.HTTP_404_NOT_FOUND}
    except ValueError as e:
        return False, {'error':f'invalid id token {e}', 'status':status.HTTP_403_FORBIDDEN}
    except auth.UnexpectedResponseError as e :
        return False, {'error':f'unexpected error {e}', 'status':status.HTTP_400_BAD_REQUEST}
    except ObjectDoesNotExist as e:
        return False, {'error':'user not found', 'status':status.HTTP_404_NOT_FOUND}
    
#delete_user deactivates a user, and verifies the users token, returns a success response to the client to delete in firebase
def delete_user(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        firebase_uid = decoded_token['uid']
        user = CustomUserV2.objects.get(firebase_uid=firebase_uid)
        user.is_active = False
        user.save()
        return True, {"success": "user deleted", 'status':status.HTTP_200_OK}
    except ValueError as e:
        return False, {'error':f'invalid id token {e}', 'status':status.HTTP_403_FORBIDDEN}
    except auth.UnexpectedResponseError as e :
        return False, {'error':f'unexpected error {e}', 'status':status.HTTP_400_BAD_REQUEST}
    except ObjectDoesNotExist as e:
        return False, {'error':'user not found', 'status':status.HTTP_404_NOT_FOUND}

#update_user takes in validated request data, and an id_token to update a users info in the DB, this only updates user info NOT password or email
def update_user(validated_data, id_token):
    username = validated_data.get('username')
    first_name = validated_data.get('first_name')
    last_name = validated_data.get('last_name')
    is_superuser = validated_data.get('is_superuser')
    is_staff = validated_data.get('is_staff')
    phone_number = validated_data.get('phone_number')
    try:
        decoded_token = auth.verify_id_token(id_token)
        firebase_uid = decoded_token['uid']
        user = CustomUserV2.objects.get(firebase_uid=firebase_uid)
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.is_superuser = is_superuser
        user.is_staff = is_staff
        user.phone_number = phone_number
        #save new user info to DB
        user.save()
        #serialize data to return in response
        user_serializer = UserSerializer(user)

        return True, {"user": user_serializer.data, 'status':status.HTTP_200_OK}
    except ValueError as e:
        return False, {'error':f'invalid id token {e}', 'status':status.HTTP_403_FORBIDDEN}
    except auth.UnexpectedResponseError as e :
        return False, {'error':f'unexpected error {e}', 'status':status.HTTP_400_BAD_REQUEST}
    except ObjectDoesNotExist as e:
        return False, {'error':'user not found', 'status':status.HTTP_404_NOT_FOUND}
