import json

import requests as rq


class Slack():
    
    def __init__(self,username,token_file):
        self.post_msg_url = 'https://slack.com/api/chat.postMessage'
        self.username = username
        self.token = open(token_file).read().strip()
         
    def send(self, channel, msg):
        headers = {'Content-Type':'application/json', 'Authorization': 'Bearer ' + self.token}
        data = {'channel':channel, 'text':msg ,'token':self.token, 'username':self.username}
        try:
            rv = rq.post(self.post_msg_url, data=json.dumps(data), headers= headers)
        except:
            return False
        if rv.status_code == 200:
            return rv.json()['ok']
        return False
    

if __name__ == '__main__':
    Slack('neutuse','slack_token.txt').send('general', 'hello from slack api')
