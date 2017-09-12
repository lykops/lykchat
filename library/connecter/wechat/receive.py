import json, time , re

from library.connecter.visit_url.cookie import Request_Url
from library.connecter.wechat import Base

class Receive_Msg(Base):
    
    '''
    接受和发送信息
    '''

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
            return (True, [])

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
        return (True, self.message_list)
