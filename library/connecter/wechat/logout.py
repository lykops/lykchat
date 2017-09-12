import json

from library.connecter.visit_url.cookie import Request_Url
from library.connecter.wechat import Base


class Logout(Base):   
    def logout(self):
        '''
        退出登录
        '''
        url = '%s/webwxlogout?redirect=1&type=0&skey=%s&sid=%s&uin=%s' % (self.mmwebwx_url, self.skey, self.sid , self.uin)
        data = {
            'sid'   : self.sid,
            'uin'   : self.uin,
            }
        data = json.dumps(data)
        open_url = Request_Url(url, data=data , **self.web_request_base_dict)
        open_url.return_context()
