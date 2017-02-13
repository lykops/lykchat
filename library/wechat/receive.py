import json, time , re

from library.visit_url.request.session import Request_Url
from .friend import Get_Friend
from .send import Send_Msg


class Receive_Msg():
    '''
    接受和发送信息
    '''
    def __init__(self, login_info, web_request_base_dict, friend_list, is_text=True):
        self.is_text = is_text
        self.web_request_base_dict = web_request_base_dict
        self.login_info = login_info
        self.skey = self.login_info['skey']
        self.sid = self.login_info['wxsid']
        self.uin = self.login_info['wxuin']
        self.deviceid = self.login_info['deviceid']
        self.synckey = self.login_info['synckey']
        self.SyncKey = self.login_info['SyncKey']
        self.sync_url = self.login_info['sync_url']
        self.pass_ticket = login_info['pass_ticket']
        self.base_url = self.login_info['url']
        self.base_request = self.login_info['BaseRequest']
        self.myself = self.login_info['myself']['UserName']
        self.friend_list = friend_list
        

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
        url_req = open_url.return_context()
        
        regx = r'window.synccheck={retcode:"(\d+)",selector:"(\d+)"}'
        pm = re.search(regx, url_req.text)

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
            # 没有新的消息
            return
        
        url = '%s/webwxsync?sid=%s&skey=%s&lang=en_US&pass_ticket=%s' % (self.base_url, self.sid, self.skey , self.pass_ticket)
        data = {
            'BaseRequest' : self.base_request,
            'SyncKey'     : self.SyncKey,
            'rr'          :~int(time.time()),
            }
    
        open_url = Request_Url(url, data=json.dumps(data) , **self.web_request_base_dict)
        url_req = open_url.return_context()
        newmessage_dict = json.loads(url_req.content.decode('utf-8', 'replace'))
        '''
        newmessage_dict
        {'DelContactCount': 0, 'ContinueFlag': 0, 'ModContactCount': 0, 'AddMsgCount': 0, 'DelContactList': [], 'ModContactList': [], 'SyncCheckKey': {'Count': 7, 'List': [{'Val': 645524181, 'Key': 1}, {'Val': 645524426, 'Key': 2}, {'Val': 645524153, 'Key': 3}, {'Val': 645524153, 'Key': 11}, {'Val': 645524153, 'Key': 13}, {'Val': 1483576562, 'Key': 1000}, {'Val': 1483576592, 'Key': 1001}]}, 'SyncKey': {'Count': 7, 'List': [{'Val': 645524181, 'Key': 1}, {'Val': 645524426, 'Key': 2}, {'Val': 645524153, 'Key': 3}, {'Val': 645524153, 'Key': 11}, {'Val': 645524153, 'Key': 13}, {'Val': 1483576562, 'Key': 1000}, {'Val': 1483576592, 'Key': 1001}]}, 'ModChatRoomMemberCount': 0, 'AddMsgList': [], 'SKey': '', 'Profile': {'BitFlag': 0, 'UserName': {'Buff': ''}, 'BindEmail': {'Buff': ''}, 'NickName': {'Buff': ''}, 'BindMobile': {'Buff': ''}, 'Status': 0, 'HeadImgUpdateFlag': 0, 'BindUin': 0, 'PersonalCard': 0, 'Signature': '', 'Alias': '', 'HeadImgUrl': '', 'Sex': 0}, 'BaseResponse': {'ErrMsg': '', 'Ret': 0}, 'ModChatRoomMemberList': []}
        '''
        
        self.login_info['SyncKey'] = newmessage_dict['SyncCheckKey']
        self.login_info['synckey'] = '|'.join(['%s_%s' % (item['Key'], item['Val'])
            for item in newmessage_dict['SyncCheckKey']['List']])

        '''
        dic['AddMsgList']，如果是文字内容如下
        接受好友信息
        {'VoiceLength': 0, 'RecommendInfo': {'VerifyFlag': 0, 'AttrStatus': 0, 'Province': '', 'Alias': '', 'QQNum': 0, 'Scene': 0, 'Content': '', 'Signature': '', 'UserName': '', 'Ticket': '', 'City': '', 'OpCode': 0, 'NickName': '', 'Sex': 0}, 'CreateTime': 1483601605, 'MsgType': 1, 'ToUserName': '@b90ca8dd73832b52edd6ff512d5393731f5a0a42379c850cce825c42d578c182', 'ImgStatus': 1, 'NewMsgId': 5543304910868065282, 'AppMsgType': 0, 'Content': '为什么', 'ForwardFlag': 0, 'AppInfo': {'Type': 0, 'AppID': ''}, 'Ticket': '', 'Status': 3, 'FileSize': '', 'HasProductId': 0, 'SubMsgType': 0, 'PlayLength': 0, 'MediaId': '', 'StatusNotifyCode': 0, 'OriContent': '', 'FileName': '', 'ImgHeight': 0, 'FromUserName': '@e3e31097fb36c1de0b6d5db44de41076a4d03a0961aca61ecfdad47950a94c59', 'Url': '', 'StatusNotifyUserName': '', 'MsgId': '5543304910868065282', 'ImgWidth': 0}
        
        发送信息给好友
        {'VoiceLength': 0, 'RecommendInfo': {'VerifyFlag': 0, 'AttrStatus': 0, 'Province': '', 'Alias': '', 'QQNum': 0, 'Scene': 0, 'Content': '', 'Signature': '', 'UserName': '', 'Ticket': '', 'City': '', 'OpCode': 0, 'NickName': '', 'Sex': 0}, 'CreateTime': 1483601472, 'MsgType': 1, 'ToUserName': '@e3e31097fb36c1de0b6d5db44de41076a4d03a0961aca61ecfdad47950a94c59', 'ImgStatus': 1, 'NewMsgId': 8659481689037786756, 'AppMsgType': 0, 'Content': '你在干嘛了', 'ForwardFlag': 0, 'AppInfo': {'Type': 0, 'AppID': ''}, 'Ticket': '', 'Status': 3, 'FileSize': '', 'HasProductId': 0, 'SubMsgType': 0, 'PlayLength': 0, 'MediaId': '', 'StatusNotifyCode': 0, 'OriContent': '', 'FileName': '', 'ImgHeight': 0, 'FromUserName': '@b90ca8dd73832b52edd6ff512d5393731f5a0a42379c850cce825c42d578c182', 'Url': '', 'StatusNotifyUserName': '', 'MsgId': '8659481689037786756', 'ImgWidth': 0}
        
        使用文件助手
        {'VoiceLength': 0, 'RecommendInfo': {'VerifyFlag': 0, 'AttrStatus': 0, 'Province': '', 'Alias': '', 'QQNum': 0, 'Scene': 0, 'Content': '', 'Signature': '', 'UserName': '', 'Ticket': '', 'City': '', 'OpCode': 0, 'NickName': '', 'Sex': 0}, 'CreateTime': 1483601523, 'MsgType': 1, 'ToUserName': 'filehelper', 'ImgStatus': 1, 'NewMsgId': 7945934153714060079, 'AppMsgType': 0, 'Content': '呵呵', 'ForwardFlag': 0, 'AppInfo': {'Type': 0, 'AppID': ''}, 'Ticket': '', 'Status': 3, 'FileSize': '', 'HasProductId': 0, 'SubMsgType': 0, 'PlayLength': 0, 'MediaId': '', 'StatusNotifyCode': 0, 'OriContent': '', 'FileName': '', 'ImgHeight': 0, 'FromUserName': '@b90ca8dd73832b52edd6ff512d5393731f5a0a42379c850cce825c42d578c182', 'Url': '', 'StatusNotifyUserName': '', 'MsgId': '7945934153714060079', 'ImgWidth': 0}
        
        进入好友
        {'VoiceLength': 0, 'RecommendInfo': {'VerifyFlag': 0, 'AttrStatus': 0, 'Province': '', 'Alias': '', 'QQNum': 0, 'Scene': 0, 'Content': '', 'Signature': '', 'UserName': '', 'Ticket': '', 'City': '', 'OpCode': 0, 'NickName': '', 'Sex': 0}, 'CreateTime': 1483601409, 'MsgType': 51, 'ToUserName': '@e3e31097fb36c1de0b6d5db44de41076a4d03a0961aca61ecfdad47950a94c59', 'ImgStatus': 1, 'NewMsgId': 3647640524784547755, 'AppMsgType': 0, 'Content': "&lt;msg&gt;<br/>&lt;op id='2'&gt;<br/>&lt;username&gt;wxid_0tinpfly0ffg21&lt;/username&gt;<br/>&lt;/op&gt;<br/>&lt;/msg&gt;", 'ForwardFlag': 0, 'AppInfo': {'Type': 0, 'AppID': ''}, 'Ticket': '', 'Status': 3, 'FileSize': '', 'HasProductId': 0, 'SubMsgType': 0, 'PlayLength': 0, 'MediaId': '', 'StatusNotifyCode': 2, 'OriContent': '', 'FileName': '', 'ImgHeight': 0, 'FromUserName': '@b90ca8dd73832b52edd6ff512d5393731f5a0a42379c850cce825c42d578c182', 'Url': '', 'StatusNotifyUserName': '@e3e31097fb36c1de0b6d5db44de41076a4d03a0961aca61ecfdad47950a94c59', 'MsgId': '3647640524784547755', 'ImgWidth': 0}
        
        '''
        message_list = newmessage_dict['AddMsgList']
        
        return 
        # 下面的先不做
    
        for message in message_list :
            self._filter_msg(message)
        

    def _filter_msg(self, message, allow_accept_userlist=[]):
        '''
        接受的信息进行过滤
        '''
        from_user = message['FromUserName']
        to_user = message['ToUserName']
        content = message['Content']
        msg_type = message['MsgType']

        if (from_user not in allow_accept_userlist and allow_accept_userlist != [])  or message['StatusNotifyUserName'] != '' or msg_type != 1 :
            # 第一个条件为from_user必须在allow_accept_userlist
            # 第二个条件为message['StatusNotifyUserName']不为空，表示用户在手机微信端上操作
            # 第三个条件为只接受文字
            return
        
        if from_user == self.myself :
            # 自己发信息
            if re.search('@@', to_user) :
                content = from_user + ':<br/>' + content
                (from_user, to_user) = (to_user, from_user)
                # 发送者和接受者转换位置 
            elif re.search('@', to_user):
                return
            else :
                if to_user == 'filehelper' :
                    pass
                else :
                    return
        else :
            if re.search('@@', from_user) or re.search(r'@', from_user) :
                pass
            else :
                # 系统信息
                return
            
        reply_dict = {'FromUser' : from_user , 'Content':content , 'ToUser' : to_user }
        self._reply_msg(reply_dict)
        

    def _reply_msg(self, reply_dict):
        '''
        回复信息
        '''
        from_user = reply_dict['FromUser']
        to_user = reply_dict['ToUser']
        content = reply_dict['Content']
        wx_friend = Get_Friend(self.login_info, self.web_request_base_dict, friend_list=self.friend_list)
        
        if re.search('@@', from_user) :
            fromuser = re.split(':' , content)[0]
            group_contact_dict = wx_friend.get_group_contact(from_user , username=fromuser)
            fromnick = group_contact_dict[fromuser]['NickName']
            fromalias = group_contact_dict[fromuser]['Alias']
            content = content.replace(fromuser + r':<br/>' , '')
            content = '昵称：' + fromnick + '，微信号：' + fromalias + '，' + content

        from_nick = wx_friend.get_friend(from_user, post_field='UserName', get_field='NickName')
        to_nick = wx_friend.get_friend(to_user, post_field='UserName', get_field='NickName')
        from_alias = wx_friend.get_friend(from_user, post_field='UserName', get_field='Alias')
        to_alias = wx_friend.get_friend(to_user, post_field='UserName', get_field='Alias')
                    
        content = '昵称：' + from_nick + '，微信号：' + from_alias + '，在' + time.strftime(' %Y-%m-%d %H:%M:%S', time.localtime()) + '，发送信息给' + '昵称：' + to_nick + '，微信号：' + to_alias + '，内容为' + content
        # print(content)
        send_msg = Send_Msg(self.login_info, self.web_request_base_dict)
        send_msg.send(content)
