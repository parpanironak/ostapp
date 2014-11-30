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

def creator_key(creator_ID):
    return ndb.Key('Creator',creator_ID)

def question_key(question_ID):
    return ndb.Key('Question',question_ID)

def answer_key(answer_ID):
    return ndb.Key('Answer',answer_ID)

def avote_key(avote_ID):
    return ndb.Key('AVote',avote_ID)

def qvote_key(qvote_ID):
    return ndb.Key('QVOte',qvote_ID)



class Question(ndb.Model):
    creator = ndb.StringProperty(indexed=True)
    qtitle = ndb.StringProperty(indexed=True)

 
class Answer(ndb.Model):
    creator = ndb.StringProperty(indexed=True)
    qid = ndb.StringProperty(indexed=True)
    answer = ndb.StringProperty(indexed=False)
    votecount = ndb.IntegerProperty(indexed=False)
    creationdatetime = ndb.DateTimeProperty(auto_now_add=True)
    date = ndb.DateProperty(auto_now_add=True)
    time = ndb.TimeProperty(auto_now_add=True)

class QVote(ndb.Model):
    creator = ndb.StringProperty(indexed=True)
    qid = ndb.StringProperty(indexed=True)
    vote = ndb.BooleanProperty(indexed = False)
      
class AVote(ndb.Model):
    creator = ndb.StringProperty(indexed=True)
    aid = ndb.StringProperty(indexed=True)
    vote = ndb.BooleanProperty(indexed = False)

class Creator(ndb.Model):
    creator = ndb.StringProperty(indexed=True)


class Main(webapp2.RedirectHandler):
    
    def get(self):
        user = users.get_current_user()
        
        guest = None
        username = None
        url = None
        if user:
            guest = False
            username = user.nickname()
        else:
            guest = True
            username = "guest"
            url = users.create_login_url("/")
        template_values = {
            'user' : username,
            'guest' : guest,
            'url' : url
        }
        template = JINJA_ENVIRONMENT.get_template("temp2.html")
        self.response.write(template.render(template_values))
        
    def post(self):
        
        a = 10


app = webapp2.WSGIApplication([
       ('/',Main),                       
    ], debug=True)