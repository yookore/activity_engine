from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from feed_engine import User
from feed_engine.models import Content


@api_view(['GET'])
def get_user(request, username):
    data = request.data
    user_name = username

    users = User.filter(username=username).allow_filtering()

    return Response(users[0], status=status.HTTP_200_OK)



#Content stuff... Will need to move out to another app

@api_view(['GET'])
def get_content(request, content_id, username): #This will have to change as we get the user from the request
    data = request.data
    content = Content.objects.get(author=username, id=content_id)

    return Response(content, status=status.HTTP_200_OK)
