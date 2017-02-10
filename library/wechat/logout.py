import json

from library.visit_url.request.session import Request_Url


class Logout():
    def __init__(self , web_request_base_dict, login_info):
        self.login_info = login_info
        self.web_request_base_dict = web_request_base_dict
        self.base_url = self.login_info['url']
        self.skey = self.login_info['skey']
        self.sid = self.login_info['wxsid']
        self.uin = self.login_info['wxuin']
        
        
    def logout(self):
        '''
        退出登录
        '''
        url = '%s/webwxlogout?redirect=1&type=0&skey=%s&sid=%s&uin=%s' % (self.base_url, self.skey, self.sid , self.uin)
        data = {
            'sid'   : self.sid,
            'uin'   : self.uin,
            }
        data = json.dumps(data)
        open_url = Request_Url(url, data=data , **self.web_request_base_dict)
        url_req = open_url.return_context()
        return url_req

'''
post

sid    
8gSB9ou/UQCiXTCS
uin    
720728179


https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxlogout?redirect=1&type=0&skey=%40crypt_de78e3c1_9b49aaee2ba81503d568ee7654a7412f&sid=8gSB9ou%2FUQCiXTCS&uin=720728179
'''
