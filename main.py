'''
Created on Nov 30, 2014

@author: Ronak
'''

import os

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

import jinja2
import webapp2
import re

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_IMAGE_NAME = "image"

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

def tag_key(qvote_ID):
    return ndb.Key('QVOte',qvote_ID)


class Question(ndb.Model):
    creator = ndb.StringProperty(indexed=True)
    qtitle = ndb.StringProperty(indexed=True)
    qdetail = ndb.StringProperty(indexed=False)
    votecount = ndb.IntegerProperty(indexed=True)
    creationdatetime = ndb.DateTimeProperty(auto_now_add=True)
    modificationdatetime = ndb.DateTimeProperty(auto_now=True)
    date = ndb.DateProperty(auto_now_add=True)
    mdate = ndb.DateProperty(auto_now=True)
    tags = ndb.StringProperty(repeated=True)
 
 
class Tag(ndb.Model): 
    tagvalue = ndb.StringProperty(indexed=True)
    
class Answer(ndb.Model):
    creator = ndb.StringProperty(indexed=True)
    qid = ndb.IntegerProperty(indexed=True)
    answer = ndb.StringProperty(indexed=False)
    votecount = ndb.IntegerProperty(indexed=False)
    creationdatetime = ndb.DateTimeProperty(auto_now_add=True)
    modificationdatetime = ndb.DateTimeProperty(auto_now=True)
    date = ndb.DateProperty(auto_now_add=True)
    mdate = ndb.DateProperty(auto_now=True)


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

class ImageData(ndb.Model):
    creator = ndb.StringProperty(indexed =True)
    imgid = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

class Main(webapp2.RedirectHandler):
    
    def get(self):
        user = users.get_current_user()
        
        isguest = None
        username = None
        url = None
        
        uploadurl = blobstore.create_upload_url('/uploadimg')
        
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
        
        link= re.compile(r'(?<!img src\=\")(https?://w*\.?(\S+)\.co\S+)')
        img = re.compile(r'(https?://\S+/(\S+)\.(jpg|jpeg|gif|png))')
        locimg = re.compile(r'(?<!")(https?://\S+/usrimg\?img_id(\S+))')
            
        
        
        
        for q in qlist:
            q.qdetail = img.sub(r'<img src="\1" alt="\2">',q.qdetail)
            q.qdetail = locimg.sub(r'<img src="\1" alt="\2">',q.qdetail)      
            q.qdetail = link.sub(r'<a href="\1">\2</a>',q.qdetail) 
            
            if q.qdetail and len(q.qdetail) > 500:
                q.qdetail = q.qdetail[:500] + "...<a href = './quest?id="+str(q.key.id())+"'>read more</a>"
            if q.qtitle and len(q.qtitle) > 50:
                q.qtitle = q.qtitle[:50] + "..."
                
        
        template_values = {
            'user' : username,
            'isguest' : isguest,
            'url' : url,
            'qlist': qlist,
            'more': nextlink,
            'ismore': more,
            'isless': less,
            'less': prevlink,
            'uploadurl':uploadurl,
        }
        template = JINJA_ENVIRONMENT.get_template("temp3.html")
        self.response.write(template.render(template_values))
        
    def post(self):
        
        user = users.get_current_user();
        if user:
            
            if self.request.get('comment'):
                tags = re.compile("[\t\n,; :]+").split(self.request.get('comment2'))
                tags2 = set()
                for tag in tags:
                    if tag == "":
                        continue;
                    else:
                        tags2.add(tag.lower());
                
                for tag in tags2:
                    t = Tag.query(Tag.tagvalue == tag).fetch();
                    if not t:
                        ta = Tag(tagvalue = tag) 
                        ta.put()
                    
                self.question = Question(creator=user.nickname(), 
                                         qtitle=self.request.get('comment'), 
                                         qdetail = self.request.get("comment1"),
                                         votecount=0,
                                         tags=tags);        
                self.question.put();
                
           
            self.redirect("/")
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
            
        link= re.compile(r'(?<!img src\=\")(https?://w*\.?(\S+)\.co\S+)')
        img = re.compile(r'(https?://\S+/(\S+)\.(jpg|jpeg|gif|png))')
        locimg = re.compile(r'(?<!")(https?://\S+/usrimg\?img_id(\S+))')
            
        
        quest.qdetail = img.sub(r'<img src="\1" alt="\2">',quest.qdetail)
        quest.qdetail = locimg.sub(r'<img src="\1" alt="\2">',quest.qdetail)      
        quest.qdetail = link.sub(r'<a href="\1">\2</a>',quest.qdetail)  

           
        for a in alist:
            a.answer = img.sub(r'<img src="\1" alt="\2">',a.answer)
            a.answer = locimg.sub(r'<img src="\1" alt="\2">',a.answer)      
            a.answer = link.sub(r'<a href="\1">\2</a>',a.answer)   
           
        template_values = {
            'user' : username,
            'isguest' : isguest,
            'url' : url,
            'question' : quest,
            'detail':quest.qdetail.strip("\""),
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
            self.redirect(self.request.referer);
            
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
        id1 = int(self.request.get('id'))
        type1 = self.request.get('type')
        
        if user: 
            
            if type1 == 'quest':
                key = question_key(id1);
                self.quest = key.get();
                
                if self.quest:
                    if str(user) == str(self.quest.creator):
                        data3 =""
                        if self.quest.tags :
                            data3 = ",".join(self.quest.tags)
                        template_values = {
                        'user': user,
                        'validuser': True,
                        'data': self.quest.qtitle,   
                        'data2': self.quest.qdetail,
                        'data3': data3,            
                        'question' : self.quest,
                        'id': id1,
                        'type': type1,
                        'cancel':self.request.referer,
                        }
                        template = JINJA_ENVIRONMENT.get_template("edit.html")
                        self.response.write(template.render(template_values))
                        
                        
            elif type1 == 'ans':    
                key = answer_key(id1);
                self.ans = key.get();
                
                if self.ans:
                    if str(user) == str(self.ans.creator):
                        
                        template_values = {
                        'user': user,
                        'validuser': True,
                        'data': self.ans.answer,               
                        'question' : self.ans,
                        'id': id1,
                        'type': type1,
                        }
                        template = JINJA_ENVIRONMENT.get_template("edit.html")
                        self.response.write(template.render(template_values))
       
        else:
            self.redirect('/');
  
    def post(self):
        user = users.get_current_user();
        id1 = int(self.request.get('id'))
        type1 = self.request.get('type') 
        data = self.request.get('data') 
        data2 = self.request.get('data2') 
        data3 = self.request.get('data3');
    
        if user:      
            if type1 == 'quest':
                key = question_key(id1);
                self.quest = key.get();
                
                if self.quest:
                    if str(user) == str(self.quest.creator):
                        self.quest.qtitle = data;
                        self.quest.qdetail = data2;
                        tags = re.compile("[\t\n,; :]+").split(data3)
                        tags2 = set()
                        
                        for tag in tags:
                            if tag == '':
                                continue;
                            
                            tags2.add(tag.lower())
                        self.quest.tags = list(tags2)
                        
                        for tag in self.quest.tags:
                            t = Tag.query(Tag.tagvalue == tag).fetch();
                            if not t:
                                t = Tag(tagvalue = tag) 
                                t.put()
                        self.quest.put()
                        self.redirect('./quest?id=%s' % id1)
                
                        
                        
            elif type1 == 'ans':    
                key = answer_key(id1);
                self.ans = key.get();
                if self.ans:
                    if str(user) == str(self.ans.creator):
                        self.ans.answer = data;
                        self.ans.put()
                        self.redirect('./quest?id=%s' % self.ans.qid)
       
        else:
            self.redirect('/');   
            
class TagPage(webapp2.RequestHandler):
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
            
        tag = self.request.get('tag');
        
                
        self.query = Question.query(Question.tags == tag).order(-Question.creationdatetime);
        
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
        
        link= re.compile(r'(?<!img src\=\")(https?://w*\.?(\S+)\.co\S+)')
        img = re.compile(r'(https?://\S+/(\S+)\.(jpg|jpeg|gif|png))')
        locimg = re.compile(r'(?<!")(https?://\S+/usrimg\?img_id(\S+))')
        
        for q in qlist:
            q.qdetail = img.sub(r'<img src="\1" alt="\2">',q.qdetail)
            q.qdetail = locimg.sub(r'<img src="\1" alt="\2">',q.qdetail)      
            q.qdetail = link.sub(r'<a href="\1">\2</a>',q.qdetail)  
            if q.qdetail and len(q.qdetail) > 500:
                q.qdetail = q.qdetail[:500] + "...<a href = './quest?id="+str(q.key.id())+"'>read more</a>"
            if q.qtitle and len(q.qtitle) > 50:
                q.qtitle = q.qtitle[:50] + "..."
                
        
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
            if self.request.get('comment'):
                tags = re.compile("[\t\n,; :]+").split(self.request.get('comment2'))
                tags2 = set()
                for tag in tags:
                    if tag == "":
                        continue;
                    else:
                        tags2.add(tag.lower());
                
                for tag in tags2:
                    t = Tag.query(Tag.tagvalue == tag).fetch();
                    if not t:
                        ta = Tag(tagvalue = tag) 
                        ta.put()
                    
                self.question = Question(creator=user.nickname(), 
                                         qtitle=self.request.get('comment'), 
                                         qdetail = self.request.get("comment1"),
                                         votecount=0,
                                         tags=tags);        
                self.question.put();
            self.redirect("/")
        else:
            url = users.create_login_url("/")
            self.redirect(url)

class GetImage(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        resource = str(self.request.get('img_id'))
        
        blob_info = blobstore.BlobInfo.get(resource)
        self.response.headers['Content-Type'] = 'image/png'
        self.send_blob(blob_info)

class UploadImage(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):        
        user = users.get_current_user()
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        
        imagedata = ImageData(parent = creator_key(user.nickname()))
        imagedata.creator = user.nickname()
        imagedata.imgid = str(blob_info.key())
        imagedata.put()
        
        self.redirect('/')
 
class ImagePage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        
        isguest = None
        username = None
        url = None
        if user:
            isguest = False
            username = user.nickname()
            url = users.create_logout_url('/')
            
            
            self.query = ImageData.query(ancestor = creator_key(user.nickname()))
            
            images = self.query.fetch()
                                                     
            if os.environ.get('HTTP_HOST'): 
                host = os.environ['HTTP_HOST'] 
            else: 
                host = os.environ['SERVER_NAME']
            
            host = self.request.host
        
            template_values = {
            'user' : username,
            'isguest' : isguest,
            'url' : url,
            'images':images,
            'host':host
            }
            
            template = JINJA_ENVIRONMENT.get_template('userimages.html')
            self.response.write(template.render(template_values))
            
        else:
            isguest = True
            username = "guest"
            url = users.create_login_url("/")
        
class GetRSS(webapp2.RequestHandler):

    def get(self):
        
        host = self.request.host
        
        self.query = Question.query().order(-Question.creationdatetime);
        
        self.quest = self.query.fetch()
       
        template_values = {
            'quest' : self.quest,   
            'host': host         
        }
        
        self.response.headers['Content-Type'] = "text/xml; charset=utf-8"
        template = JINJA_ENVIRONMENT.get_template('get_rss.rss')
        self.response.write(template.render(template_values))
            
class GetQRSS(webapp2.RequestHandler):

    def get(self):
        
        host = self.request.host
        
        if self.request.get('qid'):
            key = question_key(int(self.request.get('qid')));
            quest = key.get();
            answers = Answer.query(Answer.qid == int(self.request.get('qid'))).order(-Answer.creationdatetime)
            answers = answers.fetch()
       
            template_values = {
                'quest' : quest,
                'answer':answers,   
                'host': host         
            }
            
            self.response.headers['Content-Type'] = "text/xml; charset=utf-8"
            template = JINJA_ENVIRONMENT.get_template('getqrss.rss')
            self.response.write(template.render(template_values))
            
        self.response.write("wrong id")
                    
app = webapp2.WSGIApplication([
       ('/',Main),
       ('/quest', QuestionPage),
       ('/qvote', QVotePage),
       ('/avote', AVotePage),
       ('/uploadimg', UploadImage),
       ('/usrimg', GetImage),
       ('/edit', EditPage),  
       ('/tags',TagPage),
       ('/viewimg',ImagePage), 
       ('/getrss', GetRSS),   
       ('/getqrss', GetQRSS),                 
    ], debug=True)