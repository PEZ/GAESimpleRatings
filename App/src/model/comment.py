'''
Created on Nov 24, 2010

@author: cobpez
'''
from google.appengine.ext import db
    
class Comment(db.Model):
    created_at   = db.DateTimeProperty(auto_now_add=True)
    comment      = db.StringProperty(required=True)
    rating       = db.RatingProperty(required=True)
    tags         = db.StringListProperty(default=[])
    
    @classmethod
    def create(cls, comment, rating, tags):
        new_comment = cls(comment=comment, rating=rating, tags=tags)
        new_comment.put()
        return new_comment

    @classmethod
    def comments_for_tags(cls, tags=[], rating_threshold=8, limit=20):
        comments = cls.all().filter('rating >', rating_threshold-1)
        for tag in tags:
            comments.filter('tags =', tag)
        return [comment.comment for comment in comments.fetch(limit)]
