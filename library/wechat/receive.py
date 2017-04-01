import json, time , re

from library.visit_url.request.cookie import Request_Url

class Receive_Msg():
    '''
    接受和发送信息
    '''
    def __init__(self, session_info_dict):
        self.session_info_dict = session_info_dict
        self.web_request_base_dict = self.session_info_dict['web_request_base_dict']
        self.login_info = self.session_info_dict['login_info']
        self.skey = self.login_info['skey']
        self.sid = self.login_info['wxsid']
        self.uin = self.login_info['wxuin']
        self.deviceid = self.login_info['deviceid']
        self.synckey = self.login_info['synckey']
        self.SyncKey = self.login_info['SyncKey']
        self.sync_url = self.login_info['sync_url']
        self.pass_ticket = self.login_info['pass_ticket']
        self.base_url = self.login_info['url']
        self.base_request = self.login_info['BaseRequest']


    def _check_newmsg(self):
        '''
        用于获取最新接受信息数
        '''
        url = '%s/synccheck' % self.sync_url
        local_ts = int(time.time() * 1000)

        params = {
            'r'        : local_ts,
            'skey'     : self.skey,
            'sid'      : self.sid,
            'uin'      : self.uin,
            'deviceid' : self.deviceid,
            'synckey'  : self.synckey,
            '_'        : local_ts, }

        open_url = Request_Url(url, params=params , **self.web_request_base_dict)
        self.web_request_base_dict = self.session_info_dict['web_request_base_dict'] = open_url.return_web_request_base_dict()
        url_req = open_url.return_context()
        
        regx = r'window.synccheck={retcode:"(\d+)",selector:"(\d+)"}'
        pm = re.search(regx, url_req.text)
        '''
            retcode:
                0 正常
                1100 失败/登出微信
            selector:
                0 正常
                2 新的消息
                7 进入/离开聊天界面
        '''

        if pm is None or pm.group(1) != '0':
            return 0
        
        return pm.group(2)
    

    def receive(self):
        '''
        接受信息
        '''
        msg_no = self._check_newmsg()
        msg_no = str(msg_no)
        if msg_no == '0' :
            print('没有新的消息')
            return []

        url = '%s/webwxsync?sid=%s&skey=%s&pass_ticket=%s' % (self.base_url, self.sid, self.skey, self.pass_ticket)
        data = {
            'BaseRequest' : self.base_request,
            'SyncKey' : self.SyncKey,
            'rr' :~int(time.time()),
            }
    
        open_url = Request_Url(url, data=json.dumps(data) , **self.web_request_base_dict)
        self.web_request_base_dict = self.session_info_dict['web_request_base_dict'] = open_url.return_web_request_base_dict()
        url_req = open_url.return_context()
        newmessage_dict = json.loads(url_req.content.decode('utf-8', 'replace'))
        # 这里可以获取新信息

        self.login_info['SyncKey'] = newmessage_dict['SyncCheckKey']
        # 接收之后，会导致信息被确认查收
        self.login_info['synckey'] = ''
        for temp_dict in self.login_info['SyncKey']['List'] :
            temp = str(temp_dict['Key']) + '_' + str(temp_dict['Val'])
            if self.login_info['synckey'] == '' :
                self.login_info['synckey'] = temp
            else :
                self.login_info['synckey'] = self.login_info['synckey'] + '|' + temp

        self.message_list = newmessage_dict['AddMsgList']
        return self.message_list
