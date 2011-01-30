from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext.webapp import template

from django.utils import simplejson
import datetime
from model.rating import RaterRating
from model.comment import Comment
from model.tags import SubTag
from model.slogan import Slogan
import urllib2

from pusher.pusher_janitor import generate_connection_handshake_request,\
    make_push_rating_message
import urllib

tag_re = r'([^/]+)'
tags_re = r'(.+)'

now = datetime.datetime.now()

def admin_required(func):
    def wrapper(self, *args, **kw):
        if not users.is_current_user_admin():
            self.redirect(users.create_login_url(self.request.uri))
        else:
            func(self, *args, **kw)
    return wrapper

class WebHandler(webapp.RequestHandler):

    def Render(self, template_file, template_values, layout='main.html'):
        import os

        if layout == None:
            _template = template_file
        else:
            _template = layout
            template_values = dict(template_values, **{'template': template_file})
        path = os.path.join(os.path.dirname(__file__), 'templates', _template)
        self.response.out.write(template.render(path, template_values))

    def error(self, code):
        super(WebHandler, self).error(code)
        if code == 404:
            self.Render("404.html", {})
            
class InitRaterRatingAPIHandler(webapp.RequestHandler):
    def post(self, rater, tags):
        rater_rating = RaterRating.rating_for_rater(rater)
        if rater_rating is None:
            rater_rating = RaterRating.create([urllib.unquote(tag) for tag in tags.split('/')])
        #push_rating(rater_rating, "")
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(simplejson.dumps({'rater_id': rater_rating.rater_id, 'result': True}))

class UpdateRaterRatingAPIHandler(webapp.RequestHandler):
    def post(self, rater, rating, comment_text):
        if comment_text:
            comment_text = urllib2.unquote(comment_text)
            if type(comment_text) == type(""):
                comment_text = comment_text.decode("latin1")
        else:
            comment_text = ""
        rater_rating = RaterRating.update(rater, int(rating), comment_text)
        if rater_rating is not None:
            if comment_text != "":
                Comment.create(comment_text, int(rating), rater_rating.tags)
            self.response.out.write(simplejson.dumps({'rater_id': rater_rating.rater_id, 
                                                      'result': True,
                                                      'pusher_message':make_push_rating_message(rater_rating, comment_text)}))
        else:
            self.error(404)
            self.response.out.write(simplejson.dumps({'rater_id': None, 'result': False}))

class GetLatestRatingAPIHandler(webapp.RequestHandler):
    def get(self, days, tags):
        self.response.out.write(simplejson.dumps({'average_rating': RaterRating.average_rating_for_tags(tags.split('/'), days)}))

DEFAULT_COMMENTS_LIMIT=50
class GetLatestCommentsAPIHandler(webapp.RequestHandler):
    def get(self, tags):
        comments = Comment.comments_for_tags(tags.split('/'), DEFAULT_COMMENTS_LIMIT)
        self.response.out.write(simplejson.dumps({'comments': comments}))

class GetChannelCredentialsAPIHandler(webapp.RequestHandler):
    def get(self, rater_id, tags):
        self.response.out.write(simplejson.dumps(generate_connection_handshake_request(rater_id, [urllib.unquote(tag) for tag in tags.split('/')])))
        
def get_sub_tags(tags):
    return SubTag.sub_tags(tags.split('/'))
    
class ListSubTagsAPIHandler(webapp.RequestHandler):
    def get(self, tags):
        self.response.out.write(simplejson.dumps({'tags': [tag.tag for tag in get_sub_tags(tags)]}))

class SubTagWebHandler(WebHandler):
    @admin_required
    def get(self, tags):
        template_values = {
            'tags':  tags,
            'sub_tags': get_sub_tags(tags)
        }
        self.Render("subtags.html", template_values)

    @admin_required
    def post(self, tags):
        SubTag.create(tag=self.request.get('tag'), parent_tags=tags.split('/'))
        self.get(tags)

def get_slogans(tags):
    return Slogan.slogans_for_tags(tags.split('/'), limit=20)

class ListSlogansAPIHandler(webapp.RequestHandler):
    def get(self, tags):
        self.response.out.write(simplejson.dumps([{'text': slogan.text} for slogan in get_slogans(tags)]))

class SlogansWebHandler(WebHandler):
    @admin_required
    def get(self, tags):
        template_values = {
            'tags': tags,
            'slogans':  get_slogans(tags)
        }
        self.Render("slogans.html", template_values)

    @admin_required
    def post(self, tags):
        delete_key = self.request.get('delete');
        if delete_key:
            slogan = Slogan.get(delete_key)
            slogan.delete();
        else:
            Slogan.create(text=self.request.get('new'), tags=tags.split('/'))
        self.get(tags)
        
application = webapp.WSGIApplication([
                                      ('/sub_tags/%s' % (tags_re), SubTagWebHandler),
                                      ('/slogans/%s' % (tags_re), SlogansWebHandler),
                                      ('/api/sub_tags/%s' % tags_re, ListSubTagsAPIHandler),
                                      ('/api/slogans/%s' % tags_re, ListSlogansAPIHandler),
                                      ('/api/rater_rating/init/([0-9a-f]+)?/%s' % tags_re, InitRaterRatingAPIHandler),
                                      ('/api/rater_rating/update/([0-9a-f]+)/([1-9]|10)/(.*)', UpdateRaterRatingAPIHandler),
                                      ('/api/comments/latest/%s' % tags_re, GetLatestCommentsAPIHandler),
                                      ('/api/rating/latest/(\d+)/%s' % tags_re, GetLatestRatingAPIHandler),
                                      ('/api/channel/credentials/([0-9a-f]+)/%s' % tags_re, GetChannelCredentialsAPIHandler)
                                      ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
