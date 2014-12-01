'''
Created on Nov 30, 2014

@author: Ronak
'''

import os
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def creator_key(creator_ID):
    return ndb.Key('Creator',creator_ID)

def question_key(question_ID):
    return db.Key('Question',question_ID)

def answer_key(answer_ID):
    return ndb.Key('Answer',answer_ID)

def avote_key(avote_ID):
    return ndb.Key('AVote',avote_ID)

def qvote_key(qvote_ID):
    return ndb.Key('QVOte',qvote_ID)



class Question(ndb.Model):
    creator = ndb.StringProperty(indexed=True)
    qtitle = ndb.StringProperty(indexed=True)
    qdetail = ndb.StringProperty(indexed=False)
    votecount = ndb.IntegerProperty(indexed=True)
    creationdatetime = ndb.DateTimeProperty(auto_now_add=True)
    date = ndb.DateProperty(auto_now_add=True)
    time = ndb.TimeProperty(auto_now_add=True)

 
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
        
        isguest = None
        username = None
        url = None
        if user:
            isguest = False
            username = user.nickname()
            url = users.create_logout_url('/')
        else:
            isguest = True
            username = "guest"
            url = users.create_login_url("/")
        
        
        self.query = Question.query().order(Question.creationdatetime);
        curs = Cursor(urlsafe=self.request.get('cursor'))        
        prevcurs = self.request.get('prevcursor')        
        qlist, next_curs, more = self.query.fetch_page(5, start_cursor=curs)
        
        
        nextlink = None        
        prevlink = None
        less = False;
        
        if prevcurs:
            less = True;
            prevlink = "/?cursor=" + prevcurs
            
        elif self.request.get('cursor'):
            less = True;
            prevlink = "/"
                
        if next_curs:
            nextlink = "/?cursor=" + next_curs.urlsafe() + "&prevcursor=" +curs.urlsafe()
        
        else:
            more=False;
        
        template_values = {
            'user' : username,
            'isguest' : isguest,
            'url' : url,
            'qlist': qlist,
            'more': nextlink,
            'ismore': more,
            'isless': less,
            'less': prevlink,
        }
        template = JINJA_ENVIRONMENT.get_template("temp3.html")
        self.response.write(template.render(template_values))
        
    def post(self):
        
        user = users.get_current_user();
        if user:
            self.question = Question(creator=user.nickname(), qtitle=self.request.get('comment'), votecount=0)        
            self.question.put();
            self.redirect(self.request.referer)
        else:
            url = users.create_login_url("/")
            self.redirect(url)

class QuestionPage:
    def get(self):
        user = users.get_current_user()
        
        isguest = None
        username = None
        url = None
        if user:
            isguest = False
            username = user.nickname()
            url = users.create_logout_url('/')
        else:
            isguest = True
            username = "guest"
            url = users.create_login_url("/")  
            
        


    
        
app = webapp2.WSGIApplication([
       ('/',Main),
       ('/', QuestionPage)                       
    ], debug=True)