from .models import CustomUserV2
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
    