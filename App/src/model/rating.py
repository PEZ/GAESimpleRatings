'''
Created on Nov 24, 2010

@author: cobpez
'''
from google.appengine.ext import db
import datetime
import random
import sha
import logging

from model import Unique

    
class RaterRating(db.Model):
    created_at   = db.DateTimeProperty(auto_now_add=True)
    modified_at  = db.DateTimeProperty(auto_now=True)
    rater_id     = db.StringProperty(required=True)
    rating       = db.RatingProperty(required=True)
    comment      = db.StringProperty(required=False)
    tags         = db.StringListProperty(default=[])
    activated    = db.BooleanProperty(default=False)
    
    @classmethod
    def create_rater_id(cls):
        random.seed()
        return sha.sha("DT%s R%s" % (datetime.datetime.now(), random.random())).hexdigest()

    @classmethod
    def create(cls, tags):
        rater_id = cls.create_rater_id()
        Unique.check("rater_id", rater_id)
        rater_rating = cls(rater_id=rater_id, rating=0, comment="", tags=tags)
        rater_rating.activated = False;
        rater_rating.put()
        return rater_rating
    
    @classmethod
    def rating_for_rater(cls, rater_id):
        return cls.all().filter('rater_id =', rater_id).get()
    
    @classmethod
    def update(cls, rater_id, rating, comment):
        rater_rating = cls.rating_for_rater(rater_id)
        if rater_rating is not None:
            rater_rating.rating = rating
            rater_rating.comment = comment
            rater_rating.activated = True
            rater_rating.put()
        else:
            logging.warning("Rater id not found: %s")
        return rater_rating
    
    @classmethod
    def ratings_for_tags(cls, days=7, tags=[]):
        ratings_query = cls.all().filter('activated =', True).filter('modified_at >', datetime.datetime.now() - datetime.timedelta(days=days))
        for tag in tags:
            ratings_query.filter('tags =', tag)
        return [rating.rating for rating in ratings_query]
    
    @classmethod
    def average_rating_for_tags(cls, tags, days=7):
        ratings = cls.ratings_for_tags(int(days), tags)
        average = 0
        if ratings:
            average = float(sum(ratings)) / len(ratings)
        return average
