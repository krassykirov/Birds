from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.views import obtain_auth_token

from django.shortcuts import render,redirect,get_object_or_404,reverse
from .serializers import BirdSerializer,BirdCategorySerializer
from .forms import BirdForm,BirdImageForm,BirdSongForm,EditBirdForm
from .models import Bird,BirdImage,BirdCategory,BirdSong,BirdUser

@api_view(['GET', 'POST'])
def bird(request):
    if request.method == 'GET':  # user requesting data
        birds = Bird.objects.all()
        serializer = BirdSerializer(birds, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':  # user posting data
        serializer = BirdSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # save to db
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','DELETE'])
def bird_details(request, id):
    bird = get_object_or_404(Bird, id=id)
    if request.method == 'GET':
        serializer = BirdSerializer(bird)
        return Response(serializer.data)

    elif request.method == 'DELETE':
         # Deleting Bird Object from DB and related local image files
         bird.delete()
         return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET','POST','DELETE'])
def bird_category(request):
    if request.method == 'GET':
        categories = BirdCategory.objects.all()
        serializer = BirdCategorySerializer(categories, many=True)
        print(serializer.data)
        return Response(serializer.data)

    elif request.method == 'POST':  # user posting data
        serializer = BirdCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # save to db
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # elif request.method == 'DELETE':  # user posting data
    #     category = get_object_or_404(BirdCategory, id=id)
    #     category.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)