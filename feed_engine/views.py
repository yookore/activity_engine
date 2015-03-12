import datetime
import exceptions

from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from cassandra.cluster import Cluster
from rest_framework.response import Response
import time_uuid

from stream_framework.storage.cassandra.models import Activity
from stream_framework.verbs import get_verb_by_id
from feed_engine.feedmanager import manager
from feed_engine.models import ActivityItemModel, PaginationObject, StatusUpdate, Comment
from feed_engine.serializers import ActivityModelSerializer, ActivityRequestSerializer


cluster = Cluster(['192.168.10.200', '192.168.10.201', '192.168.10.202'])
session = cluster.connect('yookore')

# Eventually we need prepared statement for the different types
content_by_author_stmt = session.prepare("select * from content where author = ? and id = ?")
followers_statment = session.prepare("select target_user from relationships where user = ?")


def home(request):
    return render(request, 'feed_engine/home.html')


@api_view(['POST'])
@csrf_exempt
def create_activity(request):
    """
    Creates an Activity Item to be sent to user stream
    ---
    #YAML
    type:
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
          name: "ActivityObject"
          pytype: ActivityRequestSerializer
          paramType: body
          description: JSON representation of the activity item
    """
    if request.method == 'POST':
        serializer = ActivityRequestSerializer(data=request.data)
        if serializer.is_valid():
            act = serializer.data
            if act['verb_id'] != '12':
                from stream_framework.activity import Activity
                activity = Activity(
                    actor=act['author'],
                    object=act['object_id'],
                    object_type=act['object_type'],
                    verb=get_verb_by_id(int(act['verb_id'])),
                    target=act['target_id'],
                    target_type=act['target_type'],
                )
                actor = act['author']
                print act["created_at"]
                print actor, activity
                manager.addactivity_rest(actor=actor, activity=activity)

            return Response(act, status=status.HTTP_201_CREATED)
        else:
            print serializer.errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_activities(request, username, nextset=None, pointer='next'):
    """
    Retrieves the timeline for a given username earlier or later than the supplied activity id

    """
    feed = manager.get_user_feed(username)
    # feed = manager.get_feeds(username)['flat']
    print "Feed key: ", feed.key
    Activity.__table_name__ = "activities"
    paged = PaginationObject()
    paged.nextset = nextset

    if nextset is not None and pointer == 'next':
        uncapped_activities = Activity.filter(feed_id=feed.key).filter(activity_id__lt=nextset).order_by('-activity_id')
    elif nextset is not None and pointer == 'previous':
        uncapped_activities = Activity.filter(feed_id=feed.key).filter(activity_id__gt=nextset).order_by('-activity_id')
    else:
        uncapped_activities = Activity.filter(feed_id=feed.key).order_by('-activity_id')


    # activities = list(feed[:5])

    try:
        timeline = uncapped_activities[:25]
        a_id = timeline[len(timeline) - 1].activity_id
        p_id = timeline[0].activity_id
        itemlist = enrich_custom_activities(timeline)

        results = {'itemsperpage': len(timeline), 'list': itemlist,
                   'next': settings.BASE_URL + username + "/activities/next/" + str(a_id),
                   'previous': settings.BASE_URL + username + "/activities/previous/" + str(p_id)}

        return Response(results, status=status.HTTP_200_OK)
    except (IndexError) as e:
        if isinstance(e, exceptions.IndexError):
            errormsg = dict(error="No activity for the given request parameters for this user could be found")
            return Response(errormsg, status=status.HTTP_404_NOT_FOUND)
        return Response("An unknown error occurred", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_flat_activities(request, username, nextset=None, pointer='next'):
    """
    Retrieves activities for all user follows (friends and following)

    """
    feed = manager.get_feeds(username)['flat']
    print "Feed key: ", feed.key
    Activity.__table_name__ = "activities"
    paged = PaginationObject()
    paged.nextset = nextset

    if nextset is not None and pointer == 'next':
        uncapped_activities = Activity.filter(feed_id=feed.key).filter(activity_id__lt=nextset).order_by('-activity_id')
    elif nextset is not None and pointer == 'previous':
        uncapped_activities = Activity.filter(feed_id=feed.key).filter(activity_id__gt=nextset).order_by('-activity_id')
    else:
        uncapped_activities = Activity.filter(feed_id=feed.key).order_by('-activity_id')


    # activities = list(feed[:5])

    try:
        activities = uncapped_activities[:25]
        a_id = activities[len(activities) - 1].activity_id
        p_id = activities[0].activity_id
        itemlist = enrich_custom_activities(activities)

        results = {'itemsperpage': len(activities), 'list': itemlist,
                   'next': settings.BASE_URL + username + "/activities/flat/next/" + str(a_id),
                   'previous': settings.BASE_URL + username + "/activities/flat/previous/" + str(p_id)}

        return Response(results, status=status.HTTP_200_OK)
    except (IndexError) as e:
        if isinstance(e, exceptions.IndexError):
            errormsg = dict(error=e.message)
            return Response(errormsg, status=status.HTTP_404_NOT_FOUND)
        return Response("An unknown error occurred", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@csrf_exempt
def import_updates(request):
    s_update = request.data
    print s_update
    status_update = StatusUpdate()
    status_update.author = s_update['author']
    status_update.created_at = datetime.datetime.utcfromtimestamp(long(s_update['created_at']) / 1000)
    status_update.updated_at = datetime.datetime.utcfromtimestamp(long(s_update['updated_at']) / 1000)
    status_update.id = time_uuid.TimeUUID.convert(
        datetime.datetime.utcfromtimestamp(long(s_update['updated_at']) / 1000))
    status_update.body = s_update['body']
    status_update.save()
    manager.addactivity(status_update)
    print status_update

    return Response(s_update, status=status.HTTP_201_CREATED)


#
#
#
# Utility methods
#
#
# _______________________________________________________________________________________________________________________
def enrich_custom_activities(activities):
    # We need to get the enriched activities for each activity...
    # following the activity stream specs, I believe
    start_time = datetime.datetime.now()
    list = []
    for a in activities:
        # Build the activity stream object...
        print a
        activity_item = ActivityItemModel()
        # print content_by_author_stmt, a.actor, a.object
        object = session.execute(content_by_author_stmt, [a.actor, a.object])
        # print type(object)
        if len(object) > 0:

            # raise Exception(object)
            activity_item.published = object[0].created_at

            actor_object = session.execute("Select * from users where username = '" + a.actor + "'")

            # raise Exception(actor_object)

            # Actor element
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
            if content_object[0].content_type == 'statusupdate':
                activity_item.object['comments'] = settings.CONTENT_URL + "status_updates/" + str(
                    content_object[0].id) + "/comments"
            if content_object[0].content_type == 'blogpost':
                activity_item.object['comments'] = settings.CONTENT_URL + "blogposts/" + str(
                    content_object[0].id) + "/comments"

            #Updated element
            if content_object[0].updated_at:
                activity_item.updated = content_object[0].updated_at
            else:
                activity_item.updated = content_object[0].created_at

            #This block of code will get the latest comment, if any.

            lc = Comment.filter(object_id=str(content_object[0].id))[:1]

            if len(lc) > 0:
                commenter_object = session.execute("Select * from users where username = '" + lc[0].author + "'")

                if len(commenter_object) > 0:
                    #for now we assume the author always exists
                    fullname = commenter_object[0].firstname + " " + commenter_object[0].lastname
                    if commenter_object[0].profile is not None:
                        profile_pic_url = commenter_object.profile.profilepicture
                        activity_item.object['latestcomment'] = dict(author=settings.BASE_URL + "users/" + lc[0].author,
                                                                     authorname=fullname, body=lc[0].body,
                                                                     creationdate=lc[0].created_at,
                                                                     imageurl=profile_pic_url)
                    else:
                        activity_item.object['latestcomment'] = dict(author=settings.BASE_URL + "users/" + lc[0].author,
                                                                     authorname=fullname, body=lc[0].body,
                                                                     creationdate=lc[0].created_at,
                        )

                    # activity_item.object.latestcomment['body'] = lc[0].body
                    # activity_item.object.latestcomment['created_at'] = lc[0].created_at
                    #Build the comment object.

                    print "Last comment: ", lc[0]
                else:
                    activity_item.object['latestcomment'] = {}
            else:
                activity_item.object['latestcomment'] = {}
                print "No comments"

            #Target element coming soon


            serializer = ActivityModelSerializer(activity_item)
            list.append(serializer.data)
    end_time = datetime.datetime.now()
    elapsed_time = end_time - start_time
    print "Elapsed time: ", elapsed_time

    return list