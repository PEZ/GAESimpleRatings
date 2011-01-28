# -*- coding: iso-8859-1 -*-
"""
Filename:     
pp_notification_janitor.py
Description:
"""

import sha, hmac, binascii
from pusher.config import APP_ID, APP_SECRET, SERVER_URL
from django.utils.simplejson import dumps
import urllib
from google.appengine.api import urlfetch
from model.rating import RaterRating

PRIVATE_CHANNEL_PREFIX = 'private_notification'

def push_message(payload):
    form_fields = {
      "payload": dumps(payload),
    }
    form_data = urllib.urlencode(form_fields)
    urlfetch.fetch(url=SERVER_URL,
                   payload=form_data,
                   method=urlfetch.POST,
                   headers={'Content-Type': 'application/x-www-form-urlencoded'},
                   deadline=30)
    
    
def make_push_rating_message(rater_rating, comment): 
    tags = rater_rating.tags
    payloads = []
    for path in [tags[:i] for i in range(1, len(tags)+1)]:
        message = {'channelName':tags_to_channel_name(path),
                   'message':{'rating': rater_rating.rating,
                         'comment': comment,
                         'subtag' : tags[-1],
                         'rating_average': RaterRating.average_rating_for_tags(path)}}
        payloads.append(message)
    return payloads

def tags_to_channel_name(tags):
    return '/'.join(tags)

def generate_push_message(channelName, serializable):
    message = dumps(serializable)
    hobj = hmac.new(APP_SECRET, '%s_%s_%s' % (APP_ID, channelName, message), sha)
    hash_r = binascii.hexlify(hobj.digest())
    
    return {'consumerKey' : APP_ID,
              'channel' : channelName,
              'hash': hash_r,
              'sendmessage': {'message': message}}

def generate_channel_hash(rater_id, tags):
    channelName = tags_to_channel_name(tags)
    hobj = hmac.new(APP_SECRET, '%s_%s_%s' % (APP_ID, channelName, rater_id), sha)
    return binascii.hexlify(hobj.digest())

def generate_connection_handshake_request(rater_id, tags):
    channelName = tags_to_channel_name(tags)
    channelHash = generate_channel_hash(rater_id, tags)
    
    return {"channelconnect":{"channel":channelName,
                              "channelHash":channelHash,
                              "uID":rater_id,
                              "consumerKey":APP_ID}}