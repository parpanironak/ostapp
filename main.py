'''
Created on Nov 30, 2014

@author: Ronak
'''

import os
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def creator_key(creator_ID):
    return ndb.Key('Creator',creator_ID)

def question_key(question_ID):
    return ndb.Key(Question,question_ID)

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
    qid = ndb.IntegerProperty(indexed=True)
    answer = ndb.StringProperty(indexed=False)
    votecount = ndb.IntegerProperty(indexed=False)
    creationdatetime = ndb.DateTimeProperty(auto_now_add=True)
    date = ndb.DateProperty(auto_now_add=True)
    time = ndb.TimeProperty(auto_now_add=True)

class QVote(ndb.Model):
    creator = ndb.StringProperty(indexed=True)
    qid = ndb.IntegerProperty(indexed=True)
    vote = ndb.BooleanProperty(indexed = False)
      
class AVote(ndb.Model):
    creator = ndb.StringProperty(indexed=True)
    aid = ndb.IntegerProperty(indexed=True)
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
        
        
        self.query = Question.query().order(-Question.creationdatetime);
        curs = Cursor(urlsafe=self.request.get('cursor'))        
        prevcurs = self.request.get('prevcursor')        
        qlist, next_curs, more = self.query.fetch_page(10, start_cursor=curs)
        
        
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

class QuestionPage(webapp2.RequestHandler):
    
    def get(self):
        user = users.get_current_user()
        qid = int(self.request.get('id'))
        
        isguest = None
        url = None
        isguest = None
        
        
        
        if not qid:
            self.redirect('/')
        
        if user:
            isguest = False
            
            url = users.create_logout_url('/')
        else:
            isguest = True
            url = users.create_login_url("/")  
            
        
            
        key = question_key(qid);
        quest = key.get();
        
        curs = Cursor(urlsafe=self.request.get('cursor'))        
        prevcurs = self.request.get('prevcursor')    
        
        answers = Answer.query(Answer.qid == qid).order(-Answer.creationdatetime)
        alist, next_curs, more = answers.fetch_page(5, start_cursor=curs)
        
        nextlink = None        
        prevlink = None
        less = False;
        
        
        if prevcurs:
            less = True;
            prevlink = "/quest?cursor=" + prevcurs + "&id=" + str(qid)
            
        elif self.request.get('cursor'):
            less = True;
            prevlink = "/quest?id=" + str(qid)
        
        if next_curs:
            nextlink = "/quest?cursor=" + next_curs.urlsafe() + "&prevcursor=" + curs.urlsafe() + "&id=" + str(qid)
        
        else:
            more=False;
        
        username = None
        if user:
            username = user.nickname()
            
        template_values = {
            'user' : username,
            'isguest' : isguest,
            'url' : url,
            'question' : quest,
            'answers' : alist,
            'more': nextlink,
            'ismore': more,
            'isless': less,
            'less': prevlink,
        }   
         
        template = JINJA_ENVIRONMENT.get_template("quest.html")
        self.response.write(template.render(template_values))
       
    def post(self):
        user = users.get_current_user();
        qid = int(self.request.get('id'))
        
        if user:
            self.answer = Answer(creator=user.nickname(), 
                                 answer=self.request.get('comment'), 
                                 votecount=0, 
                                 qid=qid)        
            self.answer.put();
            self.redirect(self.request.referer)
            
class AVotePage(webapp2.RequestHandler):
    
    def get(self):
        user = users.get_current_user();
        aid = int(self.request.get('id'))
       
        vote = self.request.get('vote')
        
        if vote == 'True':
            vote = True;
        else:
            vote = False;
        
        if user:
            self.avote = AVote.query(ndb.AND(AVote.creator == user.nickname(), AVote.aid == aid)).get() 
            key = answer_key(aid);
            self.ans = key.get();     
            if self.avote:
                if self.avote.vote != vote:
                    self.avote.vote = vote
                    self.avote.put();
                    if vote:
                        self.ans.votecount = self.ans.votecount + 2;
                    else:
                        self.ans.votecount = self.ans.votecount - 2;
                    
                    self.ans.put()
            else:                
                self.avote = AVote(creator=user.nickname(), aid = aid, vote = vote)
                self.avote.put()
                if vote:
                        self.ans.votecount = self.ans.votecount + 1;
                else:
                        self.ans.votecount = self.ans.votecount - 1;
                
                self.ans.put()
            
        self.redirect(self.request.referer)
        

class QVotePage(webapp2.RequestHandler):
    
    def get(self):
        user = users.get_current_user();
        qid = int(self.request.get('id'))
       
        vote = self.request.get('vote')
        if vote == 'True':
            vote = True;
        else:
            vote = False;
        if user:
            self.qvote = QVote.query(ndb.AND(QVote.creator == user.nickname(), QVote.qid == qid)).get() 
            key = question_key(qid);
            self.quest = key.get();     
            if self.qvote:
                if self.qvote.vote != vote:
                    self.qvote.vote = vote
                    self.qvote.put();
                    if vote:
                        self.quest.votecount = self.quest.votecount + 2;
                    else:
                        self.quest.votecount = self.quest.votecount - 2;
                    
                    self.quest.put()
            else:                
                self.qvote = QVote(creator=user.nickname(), qid = qid, vote = vote)
                self.qvote.put()
                if vote:
                        self.quest.votecount = self.quest.votecount + 1;
                else:
                        self.quest.votecount = self.quest.votecount - 1;
                
                self.quest.put()
            
        self.redirect(self.request.referer)  
              
class EditPage(webapp2.RedirectHandler):
    def get(self):
        user = users.get_current_user();
        id = int(self.request.get('id'))
        type = self.request.get('type')
        
        if user:      
            if type == 'quest':
                key = question_key(id);
                self.quest = key.get();
                
                if self.quest:
                    if str(user) == str(self.quest.creator):
                        
                        template_values = {
                        'user': user,
                        'validuser': True,
                        'data': self.quest.qtitle,               
                        'question' : self.quest,
                        'id': id,
                        'type': type,
                        }
                        template = JINJA_ENVIRONMENT.get_template("edit.html")
                        self.response.write(template.render(template_values))
                        
                        
            elif type == 'ans':    
                key = answer_key(id);
                self.ans = key.get();
                
                if self.ans:
                    if str(user) == str(self.ans.creator):
                        
                        template_values = {
                        'user': user,
                        'validuser': True,
                        'data': self.ans.answer,               
                        'question' : self.ans,
                        'id': id,
                        'type': type,
                        }
                        template = JINJA_ENVIRONMENT.get_template("edit.html")
                        self.response.write(template.render(template_values))
       
        else:
            self.redirect('/');
            
    def post(self):
        user = users.get_current_user();
        id = int(self.request.get('id'))
        type = self.request.get('type') 
        data = self.request.get('data') 
        
        if user:      
            if type == 'quest':
                key = question_key(id);
                self.quest = key.get();
                
                if self.quest:
                    if str(user) == str(self.quest.creator):
                        self.quest.qtitle = data;
                        self.quest.put()
                        self.redirect('./quest?id=%s' % id)
                
                        
                        
            elif type == 'ans':    
                key = answer_key(id);
                self.ans = key.get();
                if self.ans:
                    if str(user) == str(self.ans.creator):
                        self.ans.answer = data;
                        self.ans.put()
                        self.redirect('./quest?id=%s' % self.ans.qid)
       
        else:
            self.redirect('/');   
            
app = webapp2.WSGIApplication([
       ('/',Main),
       ('/quest', QuestionPage),
       ('/qvote', QVotePage),
       ('/avote', AVotePage),
       ('/edit', EditPage),                    
    ], debug=True)