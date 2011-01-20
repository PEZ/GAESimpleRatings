'''
Created on Nov 24, 2010

@author: cobpez
'''
from google.appengine.ext import db
from google.appengine.ext.db import polymodel
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
    
    @classmethod
    def create_rater_id(cls):
        random.seed()
        return sha.sha("DT%s R%s" % (datetime.datetime.now(), random.random())).hexdigest()

    @classmethod
    def create(cls, rating, comment, tags):
        rater_id = cls.create_rater_id()
        Unique.check("rater_id", rater_id)
        rater_rating = cls(rater_id=rater_id, rating=rating, comment=comment, tags=tags)
        rater_rating.put()
        return rater_rating
    
    @classmethod
    def update(cls, rater_id, rating, comment):
        rater_rating = cls.all().filter('rater_id =', rater_id).get()
        if rater_rating is not None:
            rater_rating.rating = rating
            rater_rating.comment = comment
            rater_rating.put()
        else:
            logging.warning("Rater id not found: %s")
        return rater_rating
    
    @classmethod
    def ratings_for_tags(cls, days=7, tags=[]):
        ratings_query = cls.all().filter('modified_at >', datetime.datetime.now() - datetime.timedelta(days=days))
        for tag in tags:
            ratings_query.filter('tags =', tag)
        return [rating.rating for rating in ratings_query]
        

class RatingIntervalIndex(db.Model):
    created_at   = db.DateTimeProperty(auto_now_add=True)
    tags         = db.StringListProperty(default=[])
    
    @classmethod
    def construct(cls, rating_interval, tags):
        return cls(tags=tags, parent=rating_interval)

class RatingInterval(polymodel.PolyModel):
    rating  = db.RatingProperty()
    when   = db.DateTimeProperty(required=True)
    
    @classmethod
    def create(cls, rating, when, tags):
        rating_interval = cls(rating=rating, when=when)
        rating_interval.put()
        index = RatingIntervalIndex.construct(tags=tags)
        db.put(index)
        return rating_interval
    
    @classmethod
    def index_for_tags(cls, tags):
        query = RatingIntervalIndex.all(keys_only=True)
        for tag in tags:
            query.filter('tags=', tag)
        return query
