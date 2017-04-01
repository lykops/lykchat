import os
import time, sys, re

from library.config import wechat
from library.visit_url.request.cookie import Request_Url
from lykchat.settings import BASE_DIR


class Ready():
    '''
        登陆准备工作
        通过二维码，扫描、确认登陆等检测
    '''
    def __init__(self  , session_info_dict={}):
        self.os_type = wechat.os_type
        self.base_url = wechat.base_url
        self.qr_dir = wechat.qr_dir
        self.appid = wechat.appid
        
        self.session_info_dict = session_info_dict
        self.uuid = self.session_info_dict['uuid']
        self.status = self.session_info_dict['status']
        self.web_request_base_dict = self.session_info_dict['web_request_base_dict']

        if (self.uuid == '' or not self.uuid) or (not self.web_request_base_dict or self.web_request_base_dict == {}):
            web_request_base_dict = {}
            open_url = Request_Url(self.base_url, **web_request_base_dict)
            self.web_request_base_dict = open_url.return_web_request_base_dict()
        # 初始化self.web_request_base_dict，如果uuid和web_request_base_dict不为空说明已经初始化
        
        if self.uuid == '' or not self.uuid :
            self.uuid = self._get_qruuid()
            self.status = 100
        else :
            self.status = 100

        self.redirect_uri = False
        self.enablecmdqr = 1


    def _scan_qr(self):
        '''
        扫描二维码
        '''
        for count in range(10) :
            qrstorage = self.get_qr()
            if qrstorage:
                break
            elif count == 9:
                sys.exit()

    
    def check_status(self):
        '''
        检测当前状态
        关于最初status值为：
            文本界面-1
            web界面100
        '''
        status = self.status
        self.redirect_uri = ''
        count = 0
        while 1 :
            print(status)
            if status < 0 :
                self._scan_qr()
            elif status < 200 or status == 201 :
                pass
            elif status == 200 or status >= 400 :
                break
            else :
                status = 500
                break
            
            if count == 10 :
                break
            
            count += 1
            status = self._check_confirm()
            time.sleep(1)

        self.session_info_dict['status'] = status
        self.session_info_dict['redirect_uri'] = self.redirect_uri
        self.session_info_dict['web_request_base_dict'] = self.web_request_base_dict
        return self.session_info_dict


    def _check_confirm(self):
        '''
        判断是否微信用户在手机上是否点击确认，并返回一个状态吗，类似与http响应码
        '''
        url = self.base_url + '/cgi-bin/mmwebwx-bin/login'
        local_timestamp = int(time.time() * 1000)
        params = 'loginicon=true&uuid=%s&tip=0&r=%s&_=%s' % (self.uuid, -int(local_timestamp / 966), local_timestamp)
       
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

            
    def _get_qruuid(self):
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
        url = '%s/qrcode/%s' % (self.base_url, self.uuid)
        try:
            open_url = Request_Url(url, **self.web_request_base_dict)
            self.web_request_base_dict = open_url.return_web_request_base_dict()
            url_req = open_url.return_context()
        except:
            return False
        
        picdir = self.qr_dir + '/' + self.uuid + '.jpg'
        
        if os.path.exists(self.qr_dir) :
            if not os.path.isdir(self.qr_dir)  :
                os.rename(self.qr_dir, self.qr_dir + '-' + str(int(time.time)) + '-lykchat-bk')
                os.mkdir(self.qr_dir)
        else :
            os.mkdir(self.qr_dir)
        
        with open(picdir, 'wb') as f: f.write(url_req.content)

        self.session_info_dict['uuid'] = self.uuid
        self.session_info_dict['status'] = 202
        self.session_info_dict['web_request_base_dict'] = self.web_request_base_dict
        self.session_info_dict['qr_stamptime'] = int(time.time())
        self.session_info_dict['qr_url'] = picdir.replace(BASE_DIR, '')
        return self.session_info_dict
