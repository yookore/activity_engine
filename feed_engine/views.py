from django.http import HttpResponse
from django.shortcuts import render
from loremipsum import get_sentence, get_sentences
from feed_engine import StatusUpdate
from feed_engine.feedmanager import manager


def generate_activities(request):
    '''
    Lets generate mock activities for the activity stream
    :param request:
    :return: Plain text message
    '''

    counter = 0

    while counter < 100000:
        status = StatusUpdate()
        status.author = 'Carl_platt'
        status.text = get_sentence()
        status.location = 'Randburg'
        status.commentcount = 0
        status.viewcount = 0
        status.likescount = 0

        status.save()
        print status
        manager.addactivity(status)

        counter += 1

    return HttpResponse("Generating activities")