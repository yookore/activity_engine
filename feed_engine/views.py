import datetime
import random
import uuid

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from loremipsum import get_sentence
from rest_framework.renderers import JSONRenderer
from cassandra.cluster import Cluster
from stream_framework.storage.cassandra.models import Activity
from stream_framework.verbs import get_verb_by_id

from feed_engine import StatusUpdate, BlogPost, Relationship
from feed_engine.feedmanager import manager
from feed_engine.models import ActivityModel, PaginationObject
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
    return render(request, 'feed_engine/home.html', {})

def generate_activities(request, username):
    '''
    Lets generate mock activities for the activity stream
    :param request:
    :return: Plain text message
    '''

    q = Relationship.objects.filter(user=username)
    ids = []
    for rel in q:
        print rel.target_user
        ids.append(rel.target_user)
    print ids

    # result = session.execute(followers_statment, [username])
    # print(result)

    counter = 0
    usernames = ['jomski2009', 'lisanoritha', 'steveolowoyeye', 'Tomisin_fashina', 'ptchankue']
    while counter < 15:
        number = random.randint(1, 2)

        if number == 1:
            status = StatusUpdate()
            status.author = username
            status.text = get_sentence()
            status.location = 'Randburg'
            status.commentcount = random.randint(1, 999)
            status.viewcount = random.randint(1, 999)
            status.likescount = random.randint(1, 999)
            status.id = uuid.uuid1()

            status.save()
            print status
            manager.addactivity(status)

        if number == 2:
            blogpost = BlogPost()
            blogpost.author = username
            blogpost.title = get_sentence()
            blogpost.text = get_sentence()
            blogpost.commentcount = random.randint(1, 10000)
            blogpost.viewcount = random.randint(1, 999)
            blogpost.likescount = random.randint(1, 999)
            blogpost.id = uuid.uuid1()

            blogpost.save()
            print blogpost
            manager.addactivity(blogpost)

        counter += 1

    return HttpResponse("Generating activities")


@csrf_exempt
def get_activities(request, username, nextset=None, pointer='next'):
    #feed = manager.get_user_feed(username)
    feed = manager.get_feeds(username)['flat']

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
    activities = uncapped_activities[:50]
    a_id = activities[len(activities) - 1].activity_id
    p_id = activities[0].activity_id

    itemlist = enrich_custom_activities(activities)

    results = {'itemsperpage': len(activities), 'list': itemlist,
               'next': "http://localhost:8000/" + username + "/activities/next/" + str(a_id),
               'previous': "http://localhost:8000/"+username+"/activities/previous/" + str(p_id)}

    return JSONResponse(results)


@csrf_exempt
def get_flat_activities(request, username):
    flat_feed = manager.get_feeds(username)['flat']
    activities = list(flat_feed[:25])
    return JSONResponse(enrich_activities(activities))







# Utility methods
# _______________________________________________________________________________________________________________________
def enrich_activities(activities):
    # We need to get the enriched activities for each activity...
    # following the activity stream specs, I believe
    start_time = datetime.datetime.now()
    list = []
    for a in activities:
        #Build the activity stream object...
        activity_item = ActivityModel()

        object = session.execute(a_e_statement, [a.actor_id, a.object_id])
        activity_item.published = object[0].creationdate

        actor_object = session.execute("Select * from users where username = '" + a.actor_id + "'")

        #Actor element
        activity_item.actor['id'] = actor_object[0].username
        activity_item.actor['displayname'] = actor_object[0].firstname + " " + actor_object[0].lastname
        activity_item.actor['objecttype'] = 'yookos:person'
        activity_item.actor['creationdate'] = actor_object[0].creationdate
        activity_item.actor['lastprofileupdate'] = actor_object[0].lastprofileupdate
        activity_item.actor['url'] = "https://www.yookos.com/" + actor_object[0].username

        #verb element
        activity_item.verb = a.verb.past_tense

        content_object = session.execute(
            "Select * from content where author = '" + a.actor_id + "' and  id = " + str(a.object_id))

        #object element
        activity_item.object['id'] = content_object[0].id
        activity_item.object['type'] = content_object[0].content_type
        if content_object[0].title:
            activity_item.object['title'] = content_object[0].title
        if content_object[0].text:
            activity_item.object['text'] = content_object[0].text
        activity_item.object['publishdate'] = content_object[0].creationdate
        activity_item.object['likes'] = content_object[0].likescount
        activity_item.object['views'] = content_object[0].viewcount
        activity_item.object['commentcount'] = content_object[0].commentcount


        #Updated element
        if content_object[0].lastupdated:
            activity_item.updated = content_object[0].lastupdated
        else:
            activity_item.updated = content_object[0].creationdate

        #Target element coming soon


        serializer = ActivityModelSerializer(activity_item)
        list.append(serializer.data)
    end_time = datetime.datetime.now()
    elapsed_time = end_time - start_time
    print "Elapsed time: ", elapsed_time

    return list


def enrich_custom_activities(activities):
    # We need to get the enriched activities for each activity...
    # following the activity stream specs, I believe
    start_time = datetime.datetime.now()
    list = []
    for a in activities:
        #Build the activity stream object...
        activity_item = ActivityModel()

        object = session.execute(a_e_statement, [a.actor, a.object])
        activity_item.published = object[0].creationdate

        actor_object = session.execute("Select * from users where username = '" + a.actor + "'")

        #Actor element
        activity_item.actor['id'] = actor_object[0].username
        activity_item.actor['displayname'] = actor_object[0].firstname + " " + actor_object[0].lastname
        activity_item.actor['objecttype'] = 'yookos:person'
        activity_item.actor['creationdate'] = actor_object[0].creationdate
        activity_item.actor['lastprofileupdate'] = actor_object[0].lastprofileupdate
        activity_item.actor['url'] = "https://www.yookos.com/" + actor_object[0].username

        #verb element
        activity_item.verb = (get_verb_by_id(a.verb)).past_tense

        content_object = session.execute(
            "Select * from content where author = '" + a.actor + "' and  id = " + str(a.object))

        #object element
        activity_item.object['id'] = content_object[0].id
        activity_item.object['type'] = content_object[0].content_type
        if content_object[0].title:
            activity_item.object['title'] = content_object[0].title
        if content_object[0].text:
            activity_item.object['text'] = content_object[0].text
        activity_item.object['publishdate'] = content_object[0].creationdate
        activity_item.object['likes'] = content_object[0].likescount
        activity_item.object['views'] = content_object[0].viewcount
        activity_item.object['commentcount'] = content_object[0].commentcount


        #Updated element
        if content_object[0].lastupdated:
            activity_item.updated = content_object[0].lastupdated
        else:
            activity_item.updated = content_object[0].creationdate

        #Target element coming soon


        serializer = ActivityModelSerializer(activity_item)
        list.append(serializer.data)
    end_time = datetime.datetime.now()
    elapsed_time = end_time - start_time
    print "Elapsed time: ", elapsed_time

    return list