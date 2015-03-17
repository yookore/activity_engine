from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from feed_engine import User
from feed_engine.feedmanager import manager
from feed_engine.models import Content, PaginationObject
from feed_engine.views import enrich_custom_activities
from stream_framework.activity import Activity
import exceptions
from users.models import UserProfile


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


@api_view(['POST'])
def getuserprofile(request):

    data = request.data
    print data
    #We need the basic user data
    user = User.objects.get(username=data['username'])

    #We also need the user profile data
    userprofile = UserProfile.objects.get(username=data['username'])

    #Update the user profile data with user data
    # userprofile.firstname = user.firstname
    # userprofile.lastname = user.lastname
    # userprofile.email = user.email
    # userprofile.lastupdated = user.lastprofileupdate
    #userprofile.save()
    combo = dict(userdata=user, profiledata=userprofile)
    return Response(combo, status=status.HTTP_200_OK)
