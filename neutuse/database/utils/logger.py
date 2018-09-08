import logging
import logging.handlers

from neutuse.database.utils import mail, slack


class Logger():
    
    def __init__(self, logfile=None, email=None, slack=None):
        self.email = email
        self.slack = slack
        self.logger = logging.getLogger('neutuse')
        self.logger.setLevel(logging.INFO)
        logging.getLogger('werkzeug').disabled = True          
        fmt = "%(asctime)-15s %(levelname)s %(filename)s.%(lineno)d >>>> %(message)s"
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter(fmt))
        self.logger.addHandler(sh)
        if logfile:
            fh = logging.handlers.RotatingFileHandler(logfile,maxBytes = 1024*1024*100, backupCount = 3)    
            fh.setFormatter(logging.Formatter(fmt))
            self.logger.addHandler(fh)

    def info(self, msg):
        self.logger.info(msg)
        
    def warning(self, msg):
        self.logger.warning(msg)
        self._email(msg)
        self._slack(msg)
        
    def error(self, msg):
        self.logger.error(msg)
        self._email(msg)
        self._slack(msg)
    
    def _email(self, msg):
        if self.email:
            email = self.email
            host = email['host']
            user = email['user']
            passwd = email['passwd']
            port = email['port'] if 'port' in email else 25
            sender = mail.MailSender(host,user,passwd,port)
            for to in email['to']:
                sender.add_receiver(to)
            sender.set_subject('neutuse message')
            sender.add_text(msg)
            try:
                sender.send()
            except:
                pass

    def _slack(self, msg):
        if self.slack:
            token_file = self.slack['token_file']
            channel = self.slack['channel']
            slack.Slack('neutuse',token_file).send(channel, msg)
