'''
Created on Nov 30, 2014

@author: Ronak
'''

import os
from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Question(ndb.model):
    creator = ndb.StringProperty(indexed=True)
    qtitle = ndb.StringProperty(indexed=True)
    qdetail = ndb.StringProperty(indexed=False)
    vote = ndb.IntegerProperty(indexed=False)
    creationdatetime = ndb.DateTimeProperty(auto_now_add=True)
    date = ndb.DateProperty(auto_now_add=True)
    time = ndb.TimeProperty(auto_now_add=True)
    views = ndb.IntegerProperty(indexed=False)
    
class Answer(ndb.Model):
    creator = ndb.StringProperty(indexed=True)
    qtitle = ndb.StringProperty(indexed=True)
    answer = ndb.StringProperty(indexed=False)
    vote = ndb.IntegerProperty(indexed=False)
    creationdatetime = ndb.DateTimeProperty(auto_now_add=True)
    date = ndb.DateProperty(auto_now_add=True)
    time = ndb.TimeProperty(auto_now_add=True)

class Creator(ndb.Model):
    creator = ndb.StringProperty(indexed=True)
    

class Main(webapp2.RedirectHandler):
    
    def get(self):
        user = users.get_current_user()
        
        guest = None;
        username = None
        if user:
            guest = False
            username = user.nickname()
        else:
            guest = True
            username = "guest"
            
        template_values = {
            'user' : username,
            'guest' : guest
        }
        template = JINJA_ENVIRONMENT.get_template("temp.html")
        self.response.write(template.render(template_values))


app = webapp2.WSGIApplication([
       ('/',Main),                       
    ], debug=True)