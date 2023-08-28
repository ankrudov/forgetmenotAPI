from .models import Contact
from .serializers import ContactSerializer
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
#create_contact creates a contact for a user
def create_contact(validated_data):
    #get validated data
    userID = validated_data.get('user')
    contact_name = validated_data.get('name')
    phone_number = validated_data.get('phone_number')

    contact_model = Contact.objects.create(
        user = userID,
        name = contact_name,
        phone_number=phone_number
    )

    try:
        contact = Contact.objects.get(id=contact_model.id)
        contact_serializer = ContactSerializer(contact)
    except ObjectDoesNotExist as e:
        return False, {'error':'contact not found', 'status':status.HTTP_404_NOT_FOUND}
    response = {
        'response':{
            'message': f'contact: {contact_model.name} created successfully.',
            'contact': contact_serializer.data
        },
        'status': status.HTTP_201_CREATED
    }
    return True, response
