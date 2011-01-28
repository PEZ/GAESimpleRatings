'''
Created on Nov 24, 2010

@author: cobpez
'''
from google.appengine.ext import db
    
class Comment(db.Model):
    created_at   = db.DateTimeProperty(auto_now_add=True)
    comment      = db.TextProperty(required=True)
    rating       = db.RatingProperty(required=True)
    tags         = db.StringListProperty(default=[])
    
    @classmethod
    def create(cls, comment, rating, tags):
        new_comment = cls(comment=comment, rating=rating, tags=tags)
        new_comment.put()
        return new_comment

    @classmethod
    def comments_for_tags(cls, tags=[], limit=20):
        comments = cls.all()
        for tag in tags:
            comments.filter('tags =', tag)
        comments.order('-created_at')
        return [{'comment':comment.comment, 'rating':comment.rating, 'subtag': comment.tags[-1]} for comment in comments.fetch(limit)]
