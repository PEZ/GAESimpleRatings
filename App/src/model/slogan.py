'''
Created on Nov 24, 2010

@author: cobpez
'''
from google.appengine.ext import db
    
class Slogan(db.Model):
    created_at   = db.DateTimeProperty(auto_now_add=True)
    modified_at  = db.DateTimeProperty(auto_now=True)
    text         = db.TextProperty(required=True)
    tags         = db.StringListProperty(default=[])
    
    @classmethod
    def create(cls, text, tags):
        new_slogan = cls(text=text, tags=tags)
        new_slogan.put()
        return new_slogan

    @classmethod
    def slogans_for_tags(cls, tags=[], limit=20):
        slogans = cls.all()
        for tag in tags:
            slogans.filter('tags =', tag)
        slogans.order('-created_at')
        return slogans.fetch(limit) 
