import json, re
import time

from library.config import wechat 
from library.visit_url.request.cookie import Request_Url

from .friend import Get_Friend


class Send_Msg():
    '''
    接受和发送信息
    '''
    def __init__(self, session_info_dict):
        self.session_info_dict = session_info_dict
        self.login_info = self.session_info_dict['login_info']
        self.web_request_base_dict = self.session_info_dict['web_request_base_dict']
        self.base_url = self.login_info['url']
        self.base_request = self.login_info['BaseRequest']
        self.myself = self.session_info_dict['myself']
        self.msgid = int(time.time() * 1000 * 1000 * 10)


    def send(self, content, msgType='Test Message', tousername='filehelper' , post_field='UserName'):
        '''
        发送信息，返回类型为字典
        '''
        get_friend = Get_Friend(self.session_info_dict)
        friend_dict = get_friend.get_singlefriend_dict(tousername, post_field=post_field)

        try :
            tousername = friend_dict['UserName']
        except :
            tousername = ''
        
        if not re.search('@', tousername) and tousername != 'filehelper':
            return {'Msg': '发送失败，账号设置错误', 'Code':-1102, 'ErrMsg':'无法找到好友'} 
        
        url = '%s/webwxsendmsg' % self.base_url
        payloads = {
            'BaseRequest': self.base_request,
            'Msg': {
                'Type': msgType,
                'Content': content,
                'FromUserName': self.myself['UserName'],
                'ToUserName': tousername,
                'LocalID': self.msgid,
                'ClientMsgId': self.msgid,
                },
            'Scene' : 0
            }
        
        self.login_info['msgid'] += 1
        data = json.dumps(payloads, ensure_ascii=False).encode('utf8')
        open_url = Request_Url(url, data=data , **self.web_request_base_dict)
        self.web_request_base_dict = open_url.return_web_request_base_dict()
        url_req = open_url.return_context()
        
        result_dict = self._send_result(url_req)          
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
            except ValueError:
                value_dict = {
                    'BaseResponse': {
                        'Ret': -1004,
                        'ErrMsg': 'Unexpected return value', },
                    'Data': '', }

        base_response = value_dict['BaseResponse']
        # raw_msg = base_response.get('ErrMsg', '')
        result_code = base_response.get('Ret' , -1006)

        try :
            err_msg = translation_dict[language][result_code]
        except :
            err_msg = '未知错误</br>'
      
        translation_value_dict = {'Msg' : err_msg , 'Code' : result_code, 'ErrMsg' :value_dict}
  
        if result_code == 1101 :
            translation_value_dict['ResCode'] = -1
            
        return translation_value_dict
