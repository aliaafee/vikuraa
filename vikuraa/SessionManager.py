import sqlobject as sql
import sqlobject.sqlbuilder as sqlb
import socket

from datetime import datetime

class SessionManager(object):
    user = None

    def __init__(self, db):
        self.db = db
        
        
    def IsLoggedIn(self):
        if self.user == None:
            return False
            
        return True
        
        
    def Login(self, username, password):
        query = self.db.User.select(self.db.User.q.name == username)
        
        if query.count() == 1:
            result = query.getOne()
            if result.password == password:
                if 'LOGIN' in result.privilages:
                    self.user = result
                    self.loginSession()
                    return True
        return False
        
        
    def Logout(self):
        self.logoutSession()
        self.user = None
        
        
    def loginSession(self):
        now = datetime.now()
        
        newSession = self.db.Session(
            user=self.user.name, 
            time=now, 
            host=socket.gethostname(), 
            port=0)
                
        log = self.db.SessionLog(
            user=self.user.name, 
            session=newSession.id, 
            time=now, 
            host=socket.gethostname(), 
            port=0, 
            action='LOGIN')
            
        self.session = newSession
            
            
    def logoutSession(self):
        if self.session != None:
            now = datetime.now()
            
            update = sqlb.Delete('session', 
                        where=(self.db.Session.q.id == self.session.id))
            query = self.db.connection.sqlrepr(update)
            self.db.connection.query(query)
            
            log = self.db.SessionLog(
                user=self.user.name, 
                session=self.session.id, 
                time=now, 
                host=socket.gethostname(), 
                port=0, 
                action='LOGOUT')
                
            self.session = None
            
