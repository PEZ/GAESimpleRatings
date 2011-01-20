'''
Created on Nov 24, 2010

@author: cobpez
'''

from google.appengine.ext import db

class Unique(db.Model):
    @classmethod
    def check(cls, scope, value):
        def tx(scope, value):
            key_name = "U%s:%s" % (scope, value,)
            ue = Unique.get_by_key_name(key_name)
            if ue:
                raise UniqueConstraintViolation(scope, value)
            ue = Unique(key_name=key_name)
            ue.put()
        db.run_in_transaction(tx, scope, value)

class UniqueConstraintViolation(Exception):
    def __init__(self, scope, value):
        super(UniqueConstraintViolation, self).__init__("Value '%s' is not unique within scope '%s'." % (value, scope, ))