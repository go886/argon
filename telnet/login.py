# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng import EndInterrupt,Timeout,asynchronous
from chaofeng.g import mark,static
from chaofeng.ui import TextInput,Password,DatePicker
import chaofeng.ascii as ac
from argo_frame import ArgoBaseFrame,ArgoFrame
from model import manager
# from model import UserState
from datetime import datetime
import config
from collections import deque

class WelcomeViem(ArgoBaseFrame):

    _background = static['welcome'].safe_substitute(online='%(online)4s')

    @property
    def background(self):
        return self.format(self._background,online=manager.online.total_online())

    class UseridInput(TextInput):
        def acceptable(self,data):
            return data in ac.printable
    prompt = static['prompt/auth']
    _userid = UseridInput(prompt=prompt[0])
    _passwd = Password(prompt=prompt[1])

    def initialize(self):
        print 'Connect :: %s : %s' % (self.session.ip, self.session.port)
        super(WelcomeViem,self).initialize()
        # self.write_raw(ac.CMD_CHAR_PER)
        self.write(self.background)
        self.userid_ = self.load(self._userid)
        self.passwd_ = self.load(self._passwd)

    def read_userid(self):
        return self.userid_.readln()

    def read_passwd(self):
        return self.passwd_.readln()
        
@mark('welcome')
class WelcomeFrame(WelcomeViem):

    timeout = 50
    wrong_prompt = static['prompt/auth'][2]

    def initialize(self):
        super(WelcomeFrame,self).initialize()
        self.try_login_iter()

    def try_login_iter(self):
        with Timeout(self.timeout,EndInterrupt):
            while True :
                userid = self.read_userid()
                if userid == 'new' :
                    self.goto('register')
                elif userid == 'guest' :
                    self.write(u'guest用户不可用，请注册！')
                    continue
                else :
                    passwd = self.read_passwd()
                # try login
                self.try_login(userid,passwd)

    @asynchronous
    def auth(self,userid,passwd):
        authobj = manager.auth.login(userid,passwd,self.session.ip)
        if authobj :
            self.session.user = authobj
            self.session.stack = deque(maxlen=5)  #!!!!
            self.session.history = deque(maxlen=20)
        return authobj
                
    def try_login(self,userid,passwd):
        authobj = self.auth(userid,passwd)
        if authobj :
            self.goto('main')
        else:
            self.writeln(self.wrong_prompt)

    def read(self):
        res = super(WelcomeFrame, self).read()
        print repr(res)
        return res

@mark('first_login')
class FirstLoginFrame(ArgoFrame):

    def initialize(self):
        self.goto('help','index')
