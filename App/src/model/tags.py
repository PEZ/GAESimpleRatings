'''
Created on Dec 20, 2010

@author: cobpez
'''

from google.appengine.ext import db

from model import Unique

    
class SubTag(db.Model):
    parent_tags         = db.StringListProperty(default=[])
    tag                 = db.StringProperty(required=True)
    
    def stamp(self):
        return "%s/%s" % (sorted(self.parent_tags), self.tag)

    @classmethod
    def create(cls, tag, parent_tags):
        sub_tag = cls(tag=tag, parent_tags=parent_tags)
        Unique.check("sub_tag", sub_tag.stamp())
        sub_tag.put()
        return sub_tag

    @classmethod
    def sub_tags(cls, parent_tags):
        query = cls.all()
        for tag in parent_tags:
            query.filter('parent_tags =', tag)
        return list(query)