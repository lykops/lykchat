import json, time, re , random , xml.dom.minidom

from library.config import wechat
from library.visit_url.request.cookie import Request_Url


class Login():
    def __init__(self , session_info_dict):
        self.field_list = wechat.friendlist_field_list
        
        self.session_info_dict = session_info_dict
        self.login_info = self.session_info_dict['login_info']
        self.redirect_uri = self.session_info_dict['redirect_uri']
        self.web_request_base_dict = self.session_info_dict['web_request_base_dict']
        
        if not self.login_info :
            self.login_info = {}


    def init_login(self):
        '''
        扫码、点击确认之后的第一步
        '''
        if (self.redirect_uri == '' or not self.redirect_uri) and (self.login_info == {} or not self.login_info):
            self.session_info_dict['status'] = 100
            return self.session_info_dict
        
        open_url = Request_Url(self.redirect_uri, allow_redirects=False, **self.web_request_base_dict)
        self.web_request_base_dict = self.session_info_dict['web_request_base_dict'] = open_url.return_web_request_base_dict()
        url_req = open_url.return_context()
        self.login_info['url'] = self.redirect_uri[:self.redirect_uri.rfind('/')]

        domain = re.split('\/' , self.redirect_uri)[2]
        self.login_info['file_url'], self.login_info['sync_url'] = ['https://%s/cgi-bin/mmwebwx-bin' % (url + '.' + domain) for url in ("file", "webpush")]
        
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
                self.login_info['isgrayscale'] = node.childNodes[0].data
                
        if self.login_info['BaseRequest'] == {} :
            self.status = 500
            self.session_info_dict['status'] = self.status
            self.session_info_dict['login_info'] = self.login_info
            '''
            if self.login_info['ret'] == '1203' :
                print("    你的微信可能被封，请更换微信登陆或者过几小时再试")
            '''
            return self.session_info_dict
        else :
            self.session_info_dict['status'] = 221
            self.session_info_dict['login_info'] = self.login_info
            return self.session_info_dict

    
    def check_login(self):
        '''
        获得微信号登陆信息，可检测是否保持登陆成功
        '''
        self.base_url = self.login_info['url']
        self.base_request = self.login_info['BaseRequest']
        self.pass_ticket = self.login_info['pass_ticket']
        self.skey = self.login_info['skey']

        url = '%s/webwxinit?r=%s&pass_ticket=%s&skey=%s' % (self.base_url , ~int(time.time()), self.pass_ticket, self.skey)
        data = { 'BaseRequest': self.base_request }
        data = json.dumps(data)
        
        open_url = Request_Url(url, data=data, **self.web_request_base_dict)
        self.web_request_base_dict = self.session_info_dict['web_request_base_dict'] = open_url.return_web_request_base_dict()
        url_req = open_url.return_context()
        web_dict = json.loads(url_req.content.decode('utf-8', 'replace'))

        status = web_dict['BaseResponse']['Ret']
        if status == 0 :
            status = 222
        elif status == 1101 :
            status = 402
        elif status == 1205 :
            status = 404
        else :
            status = 401

        if status >= 300 :
            self.session_info_dict['status'] = status
            return self.session_info_dict

        self.myself = {}
        for key , value in web_dict.items() :
            if key == 'User' :
                # 微信号信息
                for field in self.field_list:
                    try :
                        self.myself[field] = value[field]
                    except :
                        self.myself[field] = ''
    
            if key == 'SyncKey' : 
                self.login_info[key] = web_dict[key]
                
        try : 
            if self.session_info_dict['myself']['Alias'] == '' :
                self.session_info_dict['myself'] = self.myself
        except :
            self.session_info_dict['myself'] = self.myself

        self.login_info['InviteStartCount'] = int(web_dict['InviteStartCount'])
        
        self.login_info['synckey'] = ''
        for temp_dict in self.login_info['SyncKey']['List'] :
            temp = str(temp_dict['Key']) + '_' + str(temp_dict['Val'])
            if self.login_info['synckey'] == '' :
                self.login_info['synckey'] = temp
            else :
                self.login_info['synckey'] = self.login_info['synckey'] + '|' + temp

        firstpage_contactlist = []
        for contact in web_dict['ContactList'] :
            contact_list = {}
            for field in self.field_list:
                contact_list[field] = contact[field]
            firstpage_contactlist.append(contact_list)
        self.session_info_dict['firstpage_contactlist'] = firstpage_contactlist
        # 第一页好友列表
        
        self.session_info_dict['login_info'] = self.login_info
        self.session_info_dict['status'] = status
        
        groupuser_list = self.session_info_dict['groupuser_list']
        frienduser_list = self.session_info_dict['frienduser_list']
        if (frienduser_list == [] or not frienduser_list) and (groupuser_list == [] or not groupuser_list) :
            self.webwxsync()
        return self.session_info_dict


    def status_notify(self):
        '''
        用于告知微信手机端登录状态
        '''
        self.myself = self.session_info_dict['myself']
        url = '%s/webwxstatusnotify?lang=zh_CN&pass_ticket=%s' % (self.base_url, self.pass_ticket)
        data = { 
            'BaseRequest': self.base_request,
            "Code":3,
            "FromUserName":self.myself['UserName'],
            "ToUserName":self.myself['UserName'],
            "ClientMsgId":int(time.time() * 1000 * 1000 * 10),
            }
        data = json.dumps(data)
        
        open_url = Request_Url(url, data=data, **self.web_request_base_dict)
        self.web_request_base_dict = self.session_info_dict['web_request_base_dict'] = open_url.return_web_request_base_dict()
        

    def webwxsync(self):
        '''
        获取所有的好友的UserName，用于获取群信息
        '''
        self.base_url = self.login_info['url']
        self.base_request = self.login_info['BaseRequest']
        self.pass_ticket = self.login_info['pass_ticket']
        self.skey = self.login_info['skey']
        self.sid = self.login_info['wxsid']

        url = '%s/webwxsync?sid=%s&skey=%s' % (self.base_url , self.sid, self.skey)
        
        data = { 
            'BaseRequest': self.base_request,
            'SyncKey' : self.login_info['SyncKey'] ,
            'rr' :~int(time.time())
            }
        data = json.dumps(data)
        open_url = Request_Url(url, data=data, **self.web_request_base_dict)
        url_req = open_url.return_context()
        self.web_request_base_dict = self.session_info_dict['web_request_base_dict'] = open_url.return_web_request_base_dict()
        web_dict = url_req.content.decode('utf-8', 'replace')
        web_dict = json.loads(web_dict)
        
        try :
            frienduser = web_dict['AddMsgList'][0]['StatusNotifyUserName']
            # 注意：不是每次执行会出现这个结果的，大概1%的概率
            frienduser_list = re.split(',', frienduser)
        except :
            frienduser_list = []
        
        groupuser_list = []
        for frienduser in frienduser_list :
            if re.search('@@', frienduser) :
                groupuser_list.append(frienduser)
        
        self.session_info_dict['groupuser_list'] = groupuser_list
        self.session_info_dict['frienduser_list'] = frienduser_list
        return self.session_info_dict
