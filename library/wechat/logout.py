import json

from library.visit_url.request.cookie import Request_Url


class Logout():
    def __init__(self , session_info_dict):
        self.session_info_dict = session_info_dict
        self.login_info = self.session_info_dict['login_info']
        self.web_request_base_dict = self.session_info_dict['web_request_base_dict']
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
        open_url.return_context()
