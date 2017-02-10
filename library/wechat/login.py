import json, time, re , random , xml.dom.minidom

from library.visit_url.request.session import Request_Url


class Login():
    def __init__(self , web_request_base_dict , redirect_uri='', login_info={}, is_text=True):
        if redirect_uri == '' and login_info == {}:
            return False
        
        self.is_text = is_text
        self.redirect_uri = redirect_uri
        self.login_info = login_info
        self.web_request_base_dict = web_request_base_dict
        self.emoji_regex = r'<span class="emoji emoji(.{1,10})"></span>'

        '''
        self.friend_dict = {}
        self.field_list = ['UserName', 'NickName', 'Alias', 'Sex']
        # self.field_list = ['UserName', 'NickName', 'RemarkName', 'Alias', 'RemarkPYQuanPin', 'RemarkPYInitial', 'Sex']
        # 需要的字段
        # Alias，微信号
        # RemarkName 好友备注名字
        # RemarkPYQuanPin , 好友备注名字全拼
        # RemarkPYInitial，好友备注名字拼音缩写
        '''
 
 
    def _init_login(self):
        '''
        扫码、点击确认之后的第一步
        '''
        domain = re.split('\/' , self.redirect_uri)[2]
        self.login_info['file_url'], self.login_info['sync_url'] = ['https://%s/cgi-bin/mmwebwx-bin' % (url + '.' + domain) for url in ("file", "webpush")]
        
        open_url = Request_Url(self.redirect_uri, allow_redirects=False, **self.web_request_base_dict)
        url_req = open_url.return_context()
        self.login_info['url'] = self.redirect_uri[:self.redirect_uri.rfind('/')]
        # self.login_info['url'] = self.login_info['redirect_uri'][:self.login_info['redirect_uri'].rfind('/')]
        
        self.login_info['deviceid'] = 'e' + repr(random.random())[2:17]
        self.login_info['msgid'] = int(time.time() * 1000 * 1000 * 10)
        self.login_info['BaseRequest'] = {}
        for node in xml.dom.minidom.parseString(url_req.text).documentElement.childNodes:
            if node.nodeName == 'skey':
                self.login_info['skey'] = self.login_info['BaseRequest']['Skey'] = node.childNodes[0].data
            elif node.nodeName == 'wxsid':
                self.login_info['wxsid'] = self.login_info['BaseRequest']['Sid'] = node.childNodes[0].data
            elif node.nodeName == 'wxuin':
                self.login_info['wxuin'] = self.login_info['BaseRequest']['Uin'] = node.childNodes[0].data
            elif node.nodeName == 'pass_ticket':
                self.login_info['pass_ticket'] = self.login_info['BaseRequest']['DeviceID'] = node.childNodes[0].data
            elif node.nodeName == 'ret':
                self.login_info['ret'] = node.childNodes[0].data
            elif node.nodeName == 'message':
                try :
                    self.login_info['message'] = node.childNodes[0].data
                except :
                    self.login_info['message'] = ''
            elif node.nodeName == 'isgrayscale':
                self.login_info['isgrayscale'] = self.login_info['BaseRequest']['isgrayscale'] = node.childNodes[0].data

        if self.login_info['BaseRequest'] == {} :
            self.status = 500
            if self.is_text == True :
                print('登陆失败，原因：')
                if self.login_info['ret'] == '1203' :
                    print("    你的微信可能被封，请更换微信登陆或者过几小时再试")
                else :
                    print("    未知")
            
            return False
        else :
            if self.is_text == True :
                print("登陆成功")
            return True
    
    
    def _get_wxinfo(self):
        '''
        获得微信号信息
        '''
        self.base_url = self.login_info['url']
        self.base_request = self.login_info['BaseRequest']
        self.skey = self.login_info['skey']
        self.sid = self.login_info['wxsid']
        self.uin = self.login_info['wxuin']
        self.deviceid = self.login_info['deviceid']
        self.sync_url = self.login_info['sync_url']
        self.pass_ticket = self.login_info['pass_ticket']

        url = '%s/webwxinit?r=%s' % (self.base_url, int(time.time()))
        data = { 'BaseRequest': self.base_request }
        data = json.dumps(data)
        
        open_url = Request_Url(url, data=data, **self.web_request_base_dict)
        url_req = open_url.return_context()
    
        self.web_dict = json.loads(url_req.content.decode('utf-8', 'replace'))
        '''
            web_dict的所有key为：
                ChatSet
                ContactList
                User
                ClickReportInterval
                BaseResponse
                GrayScale
                SyncKey
                SystemTime
                SKey
                ClientVersion
                InviteStartCount
                Count
                MPSubscribeMsgCount
                MPSubscribeMsgList    
        '''

        self.login_info['myself'] = {}
        for key , value in self.web_dict.items() :
            if key == 'User' :
                # 微信号信息
                for field in ['UserName', 'NickName', 'Sex']:
                    try :
                        self.login_info['myself'][field] = value[field].replace(self.emoji_regex , '')
                    except :
                        self.login_info['myself'][field] = value[field]
                        
                for field in ['Alias']:
                    self.login_info['myself'][field] = ''
    
            if key == 'SyncKey' : 
                self.login_info[key] = self.web_dict[key]
    
        self.login_info['InviteStartCount'] = int(self.web_dict['InviteStartCount'])
        self.login_info['BaseRequest'] = self.web_dict['BaseResponse']
        self.login_info['synckey'] = '|'.join(['%s_%s' % (k, v) for k, v in self.login_info['SyncKey'].items()])


    def get_logininfo(self):
        '''
        初始化获取登陆信息
        '''
        status = self._init_login()
        if not status :
            return {}
        
        self._get_wxinfo()
        return self.login_info
    
    
    def get_firstpage_contactlist(self):
        '''
        返回第一页好友列表
        '''
        self._get_wxinfo()
        return self.web_dict['ContactList']


    def check_login(self):
        '''
        检查是否在线
        '''
        self._get_wxinfo()
        return self.login_info['BaseRequest']
