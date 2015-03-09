import datetime
import random
import uuid

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from loremipsum import get_sentence
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from cassandra.cluster import Cluster
from rest_framework.response import Response

from stream_framework.storage.cassandra.models import Activity
from stream_framework.verbs import get_verb_by_id
from feed_engine import StatusUpdate, BlogPost, Relationship
from feed_engine.feedmanager import manager
from feed_engine.models import ActivityItemModel, PaginationObject
from feed_engine.serializers import ActivityModelSerializer


cluster = Cluster(['192.168.10.200', '192.168.10.201', '192.168.10.202'])
session = cluster.connect('yookore')

# Eventually we need prepared statement for the different types
a_e_statement = session.prepare("select * from content where author = ? and id = ?")
followers_statment = session.prepare("select target_user from relationships where user = ?")


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def home(request):
    return render(request, 'feed_engine/home.html')


@api_view(['POST'])
def create_activity(request):
    '''
    Creates an activity item to be fed to user streams

    And I will add some more blah blah blah here

    And it goes on and on
    ---

    type: &activity_type
        author:
            required: true
            type: string
        object_type:
            required: true
            type: string
        object_id:
            required: true
            type: string
        verb:
            required: true
            type: integer
        target_id:
            required: false
            type: string
        target_type:
            required: false
            type: string

    parameters:
    - in: body
      name: body
      description: Create an activity to be added to user feeds
      required: false
      paramType: body
      schema:
        type: *activity_type


    '''
    if request.method == 'POST':
        message = request.data
        print message
        from stream_framework.activity import Activity

        activity = Activity(
            actor=message['author'],
            object=message['object_id'],
            object_type=message['object_type'],
            verb=get_verb_by_id(int(message['verb_id'])),
            target=message['target_id'],
            target_type=message['target_type']
        )

        manager.addactivity_rest(message['author'], activity)

        return Response(message, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_activities(request, username, nextset=None, pointer='next'):
    '''
    Gets activities for a given Yookos user

    ---
    parameters_strategy: merge
    parameters:
        - name: username
          description: Username of the user
          type: string
          required: true
          paramType: path
    '''

    feed = manager.get_user_feed(username)
    # feed = manager.get_feeds(username)['flat']
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
    activities = uncapped_activities[:25]
    a_id = activities[len(activities) - 1].activity_id
    p_id = activities[0].activity_id

    itemlist = enrich_custom_activities(activities)

    results = {'itemsperpage': len(activities), 'list': itemlist,
               'next': settings.BASE_URL + username + "/activities/next/" + str(a_id),
               'previous': settings.BASE_URL + username + "/activities/previous/" + str(p_id)}

    return Response(results, status=status.HTTP_200_OK)


@csrf_exempt
def get_flat_activities(request, username):
    flat_feed = manager.get_feeds(username)['flat']
    activities = list(flat_feed[:25])
    return Response(enrich_custom_activities(activities))


# Utility methods
# _______________________________________________________________________________________________________________________
def enrich_custom_activities(activities):
    # We need to get the enriched activities for each activity...
    # following the activity stream specs, I believe
    start_time = datetime.datetime.now()
    list = []
    for a in activities:
        # Build the activity stream object...
        activity_item = ActivityItemModel()
        print a_e_statement, a.actor, a.object
        object = session.execute(a_e_statement, [a.actor, a.object])
        print type(object)
        if len(object) > 0:

            #raise Exception(object)
            activity_item.published = object[0].created_at

            actor_object = session.execute("Select * from users where username = '" + a.actor + "'")

            #raise Exception(actor_object)

            #Actor element
            activity_item.actor['id'] = actor_object[0].username
            activity_item.actor['displayname'] = actor_object[0].firstname + " " + actor_object[0].lastname
            activity_item.actor['objecttype'] = 'yookos:person'
            activity_item.actor['creationdate'] = actor_object[0].creationdate
            activity_item.actor['lastprofileupdate'] = actor_object[0].lastprofileupdate
            activity_item.actor['url'] = settings.BASE_URL + "users/" + actor_object[0].username

            #verb element
            activity_item.verb = (get_verb_by_id(a.verb)).past_tense

            content_object = session.execute(
                "Select * from content where author = '" + a.actor + "' and  id = " + str(a.object))
            #raise Exception(content_object)
            #object element
            activity_item.object['id'] = content_object[0].id
            activity_item.object['type'] = content_object[0].content_type
            if content_object[0].title:
                activity_item.object['title'] = content_object[0].title
            if content_object[0].body:
                activity_item.object['text'] = content_object[0].body
            activity_item.object['publishdate'] = content_object[0].created_at
            activity_item.object['likes'] = content_object[0].like_count
            activity_item.object['views'] = content_object[0].view_count
            activity_item.object['commentcount'] = content_object[0].comment_count
            activity_item.object['url'] = settings.BASE_URL + "content/" + actor_object[0].username + "/" + str(
                content_object[0].id)


            #Updated element
            if content_object[0].updated_at:
                activity_item.updated = content_object[0].updated_at
            else:
                activity_item.updated = content_object[0].created_at

            #Target element coming soon


            serializer = ActivityModelSerializer(activity_item)
            list.append(serializer.data)
    end_time = datetime.datetime.now()
    elapsed_time = end_time - start_time
    print "Elapsed time: ", elapsed_time

    return list


# @api_view(['GET'])
# def generate_activities(request, username):
#     '''
#     Lets generate mock activities for the activity stream
#     :param request:
#     :return: Plain text message
#     '''
#
#     q = Relationship.objects.filter(user=username)
#     ids = []
#     for rel in q:
#         print rel.target_user
#         ids.append(rel.target_user)
#     print ids
#
#     # result = session.execute(followers_statment, [username])
#     # print(result)
#
#     counter = 0
#     usernames = ['jomski2009', 'lisanoritha', 'steveolowoyeye', 'Tomisin_fashina', 'ptchankue']
#     while counter < 15:
#         number = random.randint(1, 2)
#
#         if number == 1:
#             status_update = StatusUpdate()
#             status_update.author = username
#             status_update.text = get_sentence()
#             status_update.location = 'Randburg'
#             status_update.comment_count = random.randint(1, 999)
#             status_update.view_count = random.randint(1, 999)
#             status_update.like_count = random.randint(1, 999)
#             status_update.id = uuid.uuid1()
#
#             status_update.save()
#             print status_update
#             manager.addactivity(status_update)
#
#         if number == 2:
#             blogpost = BlogPost()
#             blogpost.author = username
#             blogpost.title = get_sentence()
#             blogpost.text = get_sentence()
#             blogpost.comment_count = random.randint(1, 10000)
#             blogpost.view_count = random.randint(1, 999)
#             blogpost.like_count = random.randint(1, 999)
#             blogpost.id = uuid.uuid1()
#
#             blogpost.save()
#             print blogpost
#             manager.addactivity(blogpost)
#
#         counter += 1
#
#     return Response("Generating activities", status=status.HTTP_201_CREATED)