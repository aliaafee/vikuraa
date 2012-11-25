from datetime import datetime
from Database import Session, User, UserSession, UserSessionLog


class SessionManager(object):
    user = None

    def __init__(self):
        self.dbsession = Session()


    def __del__(self):
        self.dbsession.close()
        
        
    def IsLoggedIn(self):
        if self.user == None:
            return False
            
        return True
        
        
    def Login(self, userid, password):
        user = self.dbsession.query(User).filter(User.id == userid).first()

        print userid
        print user

        if user != None:
            if user.password == password:
                if 'LOGIN' in user.privilages:
                    self.user = user
                    self.loginSession()
                    return True
        return False
        
        
    def Logout(self):
        self.logoutSession()
        self.user = None
        
        
    def loginSession(self):
        now = datetime.now()

        self.userSession = UserSession(
            user_id=self.user.id, 
            time=now, 
            host='127.0.0.1', 
            port=0)

        self.dbsession.add(self.userSession)
        self.dbsession.commit()

        sessionlog = UserSessionLog(
            user_id=self.user.id,  
            time=now, 
            host=self.userSession.host, 
            port=self.userSession.port, 
            action='LOGIN')

        self.dbsession.add(sessionlog)
        self.dbsession.commit()
         
            
            
    def logoutSession(self):
        if self.userSession != None:
            now = datetime.now()

            sessionlog = UserSessionLog(
                user_id=self.user.id, 
                time=now, 
                host=self.userSession.host, 
                port=self.userSession.port, 
                action='LOGOUT')

            self.dbsession.add(sessionlog)

            self.dbsession.delete(self.userSession)

            self.dbsession.commit()

            self.userSession = None
