from rest_framework import serializers
from .models import *

class RegistersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registers
        exclude = ['id', 'password', 'profile_image']

class UploadsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upload
        exclude = ['id', 'password', 'profile_image']

        
