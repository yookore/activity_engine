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


@api_view(['GET'])
def get_timeline(request, username, nextset=None, pointer='next'):
    feed = manager.get_user_feed(username)
    print "Feed key: ", feed.key
    Activity.__table_name__ = "activities"
    paged = PaginationObject()
    paged.nextset = nextset

    if nextset is not None and pointer == 'next':
        uncapped_activities = Activity.filter(feed_id=feed.key).filter(activity_id__lt=nextset)
    elif nextset is not None and pointer == 'previous':
        uncapped_activities = Activity.filter(feed_id=feed.key).filter(activity_id__gt=nextset)
    else:
        uncapped_activities = Activity.filter(feed_id=feed.key)


    # activities = list(feed[:5])

    try:
        timeline = uncapped_activities[:25]
        a_id = timeline[len(timeline) - 1].activity_id
        p_id = timeline[0].activity_id
        itemlist = enrich_custom_activities(timeline)

        results = {'itemsperpage': len(timeline), 'list': itemlist,
                   'next': settings.BASE_URL + username + "/timeline/next/" + str(a_id),
                   'previous': settings.BASE_URL + username + "/timeline/previous/" + str(p_id)}

        return Response(results, status=status.HTTP_200_OK)
    except (IndexError) as e:
        if isinstance(e, exceptions.IndexError):
            errormsg = dict(error="No activity for the given request parameters for this user could be found")
            return Response(errormsg, status=status.HTTP_404_NOT_FOUND)
        return Response("An unknown error occurred", status=status.HTTP_500_INTERNAL_SERVER_ERROR)