# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header
 
 
class MailSender():
    
    def __init__(self, host, user, passwd, port=25):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.receivers = []
        self.sender = self.user
        self.text = ''
        self.subject = ''

    def set_sender(self, sender):
        self.sender = sender
        return self
        
    def add_receiver(self, receiver):
        self.receivers.append(receiver)
        return self
        
    def set_subject(self,subject):
        self.subject = subject
        
    def send(self):
        message = MIMEText(self.text, 'plain', 'utf-8')
        message['From'] = Header(self.sender)
        to = ''
        for receiver in self.receivers:
            to +=receiver
            to +=';'
        to = to[:-1]
        message['To'] =  Header(to)
        message['Subject'] = Header(self.subject, 'utf-8')
        smtpObj = smtplib.SMTP()
        smtpObj.connect(self.host, self.port)
        smtpObj.login(self.user,self.passwd)
        smtpObj.sendmail(self.user, self.receivers, message.as_string())
        return self
        
    def add_text(self, msg):
        self.text += msg

        



 


