from rest_framework import serializers
from .models import Bird,BirdImage,BirdCategory
from django.contrib.auth.models import User

class BirdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bird
        fields = ('id','bird_name', 'bird_description','photo','category')

class BirdCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BirdCategory
        fields = ['name']




