from rest_framework import serializers
from .models import Contact
import phonenumbers
from phonenumbers import NumberParseException

class ContactSerializer(serializers.ModelSerializer):
    #
    def validate_phone_number(self, value):
        if self.context['request'].method in ['POST', 'PUT']:
            try:
                phone_number = phonenumbers.parse(value, None)
                if not phonenumbers.is_possible_number(phone_number):
                    raise serializers.ValidationError("The phone number is not a possible number")
            except NumberParseException as e:
                raise serializers.ValidationError(f"error: {e}")
        return value
    
    class Meta:
        model = Contact
        fields = ['pk','user', 'name','phone_number', 'created_on', 'updated_on']