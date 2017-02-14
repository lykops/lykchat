import json, re
import time

from library.config import wechat 
from library.visit_url.request.session import Request_Url

from .friend import Get_Friend


class Send_Msg():
    '''
    接受和发送信息
    '''
    def __init__(self, login_info, web_request_base_dict):
        self.login_info = login_info
        self.web_request_base_dict = web_request_base_dict
        # self.skey = self.login_info['skey']
        # self.sid = self.login_info['wxsid']
        # self.uin = self.login_info['wxuin']
        # self.deviceid = self.login_info['deviceid']
        # self.synckey = self.login_info['synckey']
        # self.SyncKey = self.login_info['SyncKey']
        # self.sync_url = self.login_info['sync_url']
        # self.pass_ticket = login_info['pass_ticket']
        self.base_url = self.login_info['url']
        self.base_request = self.login_info['BaseRequest']
        self.myself = self.login_info['myself']['UserName']
        self.msgid = int(time.time() * 1000 * 1000 * 10)


    def send(self, content, msgType='Test Message', tousername='filehelper' , post_field='UserName'):
        '''
        发送信息，返回类型为字典
        '''
        get_friend = Get_Friend(self.login_info, self.web_request_base_dict)
        friend_dict = get_friend.get_singlefriend_dict(tousername, post_field=post_field)

        try :
            tousername = friend_dict['UserName']
        except :
            tousername = ''
        
        if not re.search('@', tousername) and tousername != 'filehelper':
            return {'RawErr': '', 'ErrMsg': '发送失败，账号设置错误', 'ResultCode':-1005, 'content': content, 'tousername':tousername, 'touser': ''} 
        
        url = '%s/webwxsendmsg' % self.base_url
        payloads = {
            'BaseRequest': self.base_request,
            'Msg': {
                'Type': msgType,
                'Content': content,
                'FromUserName': self.myself,
                'ToUserName': tousername,
                'LocalID': self.msgid,
                'ClientMsgId': self.msgid,
                },
            'Scene' : 0
            }
        
        self.login_info['msgid'] += 1
        data = json.dumps(payloads, ensure_ascii=False).encode('utf8')
        open_url = Request_Url(url, data=data , **self.web_request_base_dict)
        url_req = open_url.return_context()
        
        result_dict = self._send_result(url_req)
        result_dict['content'] = content
        '''
        result_dict['tousername'] = tousername
        # 接受者用户名，例如@b90ca8dd73832b52edd6ff512d5393731f5a0a42379c850cce825c42d578c182
        alias = friend_dict['Alias']
        nickname = friend_dict['NickName']
        remarkname = friend_dict['RemarkName']
        
        if alias == '' or not alias :
            if remarkname == '' or not remarkname :
                result_dict['touser'] = '昵称：' + nickname
            else :
                result_dict['touser'] = '昵称：' + nickname + '--备注：' + remarkname
        else :
            if remarkname == '' or not remarkname :
                result_dict['touser'] = '昵称：' + nickname + '--微信号：' + alias
            else :
                result_dict['touser'] = '昵称：' + nickname + '--备注：' + remarkname + '--微信号：' + alias
        '''
                
        result_dict['friend_dict'] = friend_dict
                        
        return result_dict


    def _send_result(self, send_result):
        '''
        返回发送信息结果，返回类型为字典
        '''
        value_dict = {}
        language = wechat.language
        translation_dict = wechat.sendresult_translation_dict
        
        if send_result:
            try:
                value_dict = send_result.json()
                # {'MsgID': '2767920227301597012', 'BaseResponse': {'Ret': 0, 'ErrMsg': ''}, 'LocalID': '1482062133882'}
            except ValueError:
                value_dict = {
                    'BaseResponse': {
                        'Ret': -1004,
                        'ErrMsg': 'Unexpected return value', },
                    'Data': '', }

        base_response = value_dict['BaseResponse']
        raw_msg = base_response.get('ErrMsg', '')
        result_code = base_response.get('Ret' , -1006)

        try :
            err_msg = translation_dict[language][result_code]
        except :
            err_msg = '未知错误</br>'
      
        translation_value_dict = {'RawErr' : raw_msg , 'ErrMsg' : err_msg , 'ResultCode' : result_code, 'RawMsg' :value_dict}
  
        if result_code == 1101 :
            translation_value_dict['ResCode'] = -1
  
        return translation_value_dict
