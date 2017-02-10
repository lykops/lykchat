import io, time, sys, re

from library.config import wechat
from library.visit_url.request.session import Request_Url

from .qr_code import print_qr


class Ready():
    '''
        登陆准备工作
        通过二维码，扫描、确认登陆等检测

    '''
    def __init__(self  , uuid='', web_request_base_dict={}, is_text=True):
        # 参数is_text表示是否是命令行运行该项目
        self.is_text = is_text
        self.base_url = wechat.base_url
        self.qr_dir = wechat.qr_dir

        if uuid == '' or web_request_base_dict == {}:
            open_url = Request_Url(self.base_url, **web_request_base_dict)
            self.web_request_base_dict = open_url.return_web_request_base_dict()
        else :
            self.web_request_base_dict = web_request_base_dict
        # 初始化self.web_request_base_dict，如果uuid和web_request_base_dict不为空说明已经初始化
        
        self.os_type = wechat.os_type
        if uuid == '' or not uuid :
            self.uuid = self._get_qruuid()
            if  is_text == True :
                self.status = -1
            else :
                self.status = 100
            # 调用时uuid为空，登陆状态为-1(文本模式为0，web模式为100)，带uuid时状态为100
        else :
            self.uuid = uuid
            self.status = 100

        self.redirect_uri = False
        self.enablecmdqr = 1
   

    def return_basicinfo_dict(self):
        return (self.uuid, self.web_request_base_dict)


    def _scan_qr(self):
        '''
        扫描二维码
        '''
        for count in range(10) :
            if self.is_text == True :
                print('请扫描二维码登陆')
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
            elif status < 200:
                pass
            elif status == 201 :
                if self.is_text == True :
                    print('请在微信上点击确认登陆')
            elif status == 200 :
                if self.is_text == True :
                    print('确认成功或者已经登陆')
                break
            elif status < 500 and status >= 400 :
                if self.is_text == True :
                    print('登陆失效，请重新登陆')
                break
                # self.uuid = self._get_qruuid()
                # self._scan_qr()
            else :
                status = 500
                break
            
            if count == 5 :
                break
            
            count += 1
            status = self._check_confirm()
            time.sleep(1)
            
        return (status, self.redirect_uri)


    def _check_confirm(self):
        '''
        判断是否微信用户在手机上是否点击确认，并返回一个状态吗，类似与http响应码
        '''
        url = self.base_url + '/cgi-bin/mmwebwx-bin/login'
        local_timestamp = int(time.time())
        params = 'loginicon=true&uuid=%s&tip=0&r=%s&_=%s' % (self.uuid, -int(local_timestamp / 1524), local_timestamp)
       
        open_url = Request_Url(url, params=params, **self.web_request_base_dict)
        url_context = open_url.return_context()
        regx = r'window.code=(\d+)'
        data = re.search(regx, url_context.text)

        if data and data.group(1) == '200':
            # self.login_info['context'] = url_context.text
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
        local_timestamp = int(time.time())
        params = {
            'appid' : 'wx782c26e4c19acffb',
            'fun'   : 'new',
            'lang' : 'en_US',
            'redirect_uri' : 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage' ,
            '_' : local_timestamp
            }
        
        open_url = Request_Url(url, params=params, **self.web_request_base_dict)
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
            url_req = open_url.return_context()
        except:
            return False
        
        picdir = self.qr_dir + '/' + self.uuid + '.jpg'
        qrstorage = io.BytesIO(url_req.content)
        
        with open(picdir, 'wb') as f: f.write(url_req.content)
        if self.is_text == True :
            print_qr(picdir, enablecmdqr=self.enablecmdqr)
            return qrstorage
        else :
            return picdir
