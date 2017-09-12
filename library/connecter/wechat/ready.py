import time, re

from library.connecter.visit_url.cookie import Request_Url
from library.connecter.wechat import Base
from library.utils.path import make_dir

class Ready(Base):
    
    '''
        登陆准备工作
        通过二维码，扫描、确认登陆等检测
    '''

    def check_status(self):
        
        '''
        检测当前状态
        '''

        self.uuid = self.session_info_dict.get('uuid', '')
        status = self.session_info_dict.get('status', 100)
        if not self.web_request_base_dict or not self.uuid:      
            return (False, '请先获取二维码')

        count = 0
        while 1 :
            if status < 200 :
                pass
            if status == 201 :
                pass
            elif status == 200 :
                pass
            elif status >= 400 :
                break
            # else :
            #    status = 500
            #    break
            
            if count == 10 :
                break
            
            count += 1
            status = self._check_confirm()
            time.sleep(1)

        self.session_info_dict['status'] = status
        self.session_info_dict['redirect_uri'] = self.redirect_uri
        self.session_info_dict['web_request_base_dict'] = self.web_request_base_dict
        return (True, self.session_info_dict)


    def _check_confirm(self):
        
        '''
        判断是否微信用户在手机上是否点击确认，并返回一个状态吗，类似与http响应码
        '''
        
        url = self.base_url + '/cgi-bin/mmwebwx-bin/login'
        local_timestamp = time.time()
        params = 'loginicon=true&uuid=%s&tip=0&r=%s&_=%s' % (self.uuid, ~int(local_timestamp), local_timestamp * 1000)
       
        open_url = Request_Url(url, params=params, **self.web_request_base_dict)
        self.web_request_base_dict = open_url.return_web_request_base_dict()
        url_context = open_url.return_context()
        regx = r'window.code=(\d+)'
        data = re.search(regx, url_context.text)

        if data and data.group(1) == '200':
            regx = r'window.redirect_uri="(\S+)";'
            self.redirect_uri = re.search(regx, url_context.text).group(1)
            # 登陆成功之后，获取用户信息页面

            return 200
            # 200确认按钮点击成功
        elif data and data.group(1) == '201':
            return 201
            # 201  手机扫描识别成功
        else:
            try :
                return int(data.group(1))
            except :
                return 500

            
    def get_qruuid(self):
        
        '''
        获取登陆时二维码uuid
        '''
        
        url = self.base_url + '/jslogin'
        local_timestamp = int(time.time()*1000)
        params = {
            'appid' :self.appid,
            'fun'   : 'new',
            'lang' : 'zh_CN',
            'redirect_uri' : self.base_url + '/cgi-bin/mmwebwx-bin/webwxnewloginpage' ,
            '_' : local_timestamp
            }
        
        open_url = Request_Url(url, params=params, **self.web_request_base_dict)
        self.web_request_base_dict = open_url.return_web_request_base_dict()
        url_req = open_url.return_context()
        regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)";'
        data = re.search(regx, url_req.text)

        if data and data.group(1) == '200':
            return data.group(2)
        else :
            return 


    def get_qr(self):
        
        '''
        根据uuid获取二维码
        '''
        
        if not self.web_request_base_dict:
            open_url = Request_Url(self.base_url, {})
            self.web_request_base_dict = open_url.return_web_request_base_dict()
        # 初始化self.web_request_base_dict
        
        if self.uuid is None :
            uuid = self.get_qruuid()
        
        url = '%s/qrcode/%s' % (self.base_url, uuid)
        try:
            open_url = Request_Url(url, **self.web_request_base_dict)
            self.web_request_base_dict = open_url.return_web_request_base_dict()
            url_req = open_url.return_context()
        except:
            return (False, '获取二维码失败')
        
        picdir = self.qr_dir + '/' + uuid + '.jpg'
        make_dir(self.qr_dir, chmods=755 , force=True , backup=True)
        with open(picdir, 'wb') as f: f.write(url_req.content)

        self.session_info_dict['uuid'] = uuid
        self.session_info_dict['status'] = 202
        self.session_info_dict['web_request_base_dict'] = self.web_request_base_dict
        self.session_info_dict['qr_stamptime'] = int(time.time())
        self.session_info_dict['start_timestamp'] = int(time.time())
        self.session_info_dict['qr_url'] = picdir.replace(self.base_dir, '')
        
        return (True, self.session_info_dict)
