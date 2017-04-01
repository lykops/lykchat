import json, time, re

from library.config import wechat
from library.visit_url.request.cookie import Request_Url


class Get_Friend():
    def __init__(self , session_info_dict):
        self.field_list = wechat.friendlist_field_list
        
        self.session_info_dict = session_info_dict
        self.login_info = self.session_info_dict['login_info']
        
        try :
            self.friend_list = self.session_info_dict['friend_list']
        except :
            self.friend_list = {}

        if self.friend_list == {} or not self.friend_list :
            for field in self.field_list:
                self.friend_list[field] = []
            
        self.web_request_base_dict = self.session_info_dict['web_request_base_dict'] 
        self.base_url = self.login_info['url']
        self.base_request = self.login_info['BaseRequest']
        self.pass_ticket = self.login_info['pass_ticket']
        self.skey = self.login_info['skey']
        self.firstpage_contactlist = self.session_info_dict['firstpage_contactlist']
        self.groupuser_list = self.session_info_dict['groupuser_list']
        
        
    def get_friend_list(self):
        '''
        获得所有好友信息，返回好友清单
        格式如下：
            {
                'UserName':['@aafadfd','@bbbbbb',....],
                'NickName':['lykops','ops',....]
                'Alias':['lykops','ops',....]
                'Sex':[1,2,...]
            }
        '''
        url = '%s/webwxgetcontact?r=%s&seq=0&skey=%s' % (self.base_url, int(time.time() * 1000), self.skey)

        open_url = Request_Url(url, **self.web_request_base_dict)
        self.web_request_base_dict = self.session_info_dict['web_request_base_dict'] = open_url.return_web_request_base_dict()
        url_req = open_url.return_context()
    
        member_list = json.loads(url_req.content.decode('utf-8', 'replace'))['MemberList']
        '''
            [{'RemarkPYQuanPin': '', 'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=645115088&username=@4f9f900c9207f0d6d1e104ed99561de1&skey=@crypt_2b05caf0_8cef13f418418c2333f2cb1a3b3172e1', 'AppAccountFlag': 0, 'Statues': 0, 'SnsFlag': 0, 'AttrStatus': 0, 'PYQuanPin': 'gaoxiaokaifayunwei', 'City': 'Chaoyang', 'HideInputBarFlag': 0, 'ContactFlag': 3, 'Uin': 0, 'Sex': 0, 'PYInitial': 'GXKFYW', 'OwnerUin': 0, 'RemarkName': '', 'Alias': 'DevOpsGeek', 'Signature': 'InfoQ。~', 'KeyWord': 'gh_', 'RemarkPYInitial': '', 'UniFriend': 0, 'UserName': '@4f9f900c9207f0d6d1e104ed99561de1', 'ChatRoomId': 0, 'MemberCount': 0, 'Province': 'Beijing', 'DisplayName': '', 'NickName': '高效开发运维', 'VerifyFlag': 24, 'EncryChatRoomId': '', 'StarFriend': 0, 'MemberList': []}]
            sex:
                1为男
                2为女
                0为其他
        '''
     
        for field in self.field_list:
            self.friend_list[field] = []
        # 需要清空，否则在web页面上登陆后，不更新程序时，出现旧数据不会并删除
            
        for friend_message in member_list :
            self._update_friend(friend_message)
        
        self._update_myself()
        # 更新个人信息
        
        self.session_info_dict['friend_list'] = self.friend_list
        return self.session_info_dict


    def get_singlefriend_dict(self, friend, post_field='UserName'):
        '''
        好友信息进行转化，把现有字段post_field转化从字典
        '''        
        if self.friend_list == {} or not self.friend_list :
            self.friend_list = self.get_friend_list()
        
        if post_field in self.field_list :
            pass
        else :
            return {}
        
        if friend == '':
            return {}
        
        try :
            friend_index = self.friend_list[post_field].index(friend)
        except :
            try :
                self.friend_list = self.update_friend_list()
                friend_index = self.friend_list[post_field].index(friend)
            except :
                return {}
            
        friend_dict = {}
        for field in self.field_list:
            friend_dict[field] = self.friend_list[field][friend_index]

        return friend_dict


    def update_friend_list(self):
        '''
        通过微信第一页好友列表获取好友，追加好友
        '''
        for contact in self.firstpage_contactlist :
            self._update_friend(contact) 
            
        self._update_myself()
        # 更新个人信息
            
        self.session_info_dict['friend_list'] = self.friend_list
        return self.session_info_dict
    
    
    def get_group_contact(self, group_username , username='' , username_list=[]):
        '''
        根据群的username和成员的username，获得成员信息
        '''
        url = '%s/webwxbatchgetcontact?type=ex&r=%s&lang=zh_CN&pass_ticket=%s' % (self.base_url, int(time.time() * 1000), self.pass_ticket)
        post_list = []
        
        if group_username == '' or not group_username or not re.search('@@', group_username):
            return {}
        
        if username_list != [] :
            for username in username_list : 
                temp = {"UserName":username, "EncryChatRoomId":group_username}
                post_list.append(temp)
                list_count = len(username_list)
        else :
            if username and re.search('@' , username):
                temp = {"UserName":username, "EncryChatRoomId":group_username}
                post_list.append(temp)
                list_count = 1
            else :
                return {}
            
        data = {
            'BaseRequest' : self.base_request,
            'List'        : post_list,
            'Count'       : list_count,
            }
        
        open_url = Request_Url(url, data=json.dumps(data) , **self.web_request_base_dict)
        self.web_request_base_dict = self.session_info_dict['web_request_base_dict'] = open_url.return_web_request_base_dict()
        url_req = open_url.return_context()
        web_dict = json.loads(url_req.content.decode('utf-8', 'replace')) 
        contact_list = web_dict['ContactList']

        group_contact_dict = {}
        for contact in contact_list :
            group_contact_dict[username] = {'UserName':username , 'Alias' : contact['Alias'], 'NickName' : contact['NickName'], 'Sex' : contact['Sex']}
                
            # 更新好友列表
            self._update_friend(group_contact_dict[username])
                    
        return group_contact_dict


    def _update_myself(self):
        '''
        通过群获取登陆微信号的信息
        '''
        myself = self.session_info_dict['myself']
        my_user = myself['UserName']
        my_alias = myself['Alias']
        my_nick = myself['NickName']
        
        if (not my_alias or my_alias == '') or (not my_nick or my_nick == '') :
            try :
                group_username = self.groupuser_list[0]
            except  : 
                for contact in self.firstpage_contactlist :
                    if re.search('@@' , contact['UserName']) :
                        group_username = contact['UserName']
                        break
                    else :
                        group_username = False
        
            if group_username and re.search('@@' , group_username) :
                group_contact_dict = self.get_group_contact(group_username, username=my_user)
                if group_contact_dict != {} and group_contact_dict:
                    my_nick = group_contact_dict[my_user]['NickName']
                    my_alias = group_contact_dict[my_user]['Alias']

        self.session_info_dict['myself']['Alias'] = my_alias
        self.session_info_dict['myself']['NickName'] = my_nick
        self.session_info_dict['myself']['UserName'] = my_user
        return self.session_info_dict['myself']


    def _update_friend(self, friend_dict): 
        '''
        向好友列表中更新单个好友信息
        '''
        user = friend_dict['UserName']
        if user in self.friend_list['UserName']:
            user_index = self.friend_list['UserName'].index(user)
            self.friend_list['Alias'][user_index] = friend_dict['Alias']
            self.friend_list['NickName'][user_index] = friend_dict['NickName']
            self.friend_list['Sex'][user_index] = friend_dict['Sex']
            try :
                self.friend_list['RemarkName'][user_index] = friend_dict['RemarkName']
            except :
                self.friend_list['RemarkName'][user_index] = ''
        else :
            for field in self.field_list:
                try :
                    value = friend_dict[field]
                except :
                    value = ''
                self.friend_list[field].append(value)


    def get_friend_dict(self):
        '''
        用于web页面展示
        '''
        try :
            username_list = self.friend_list['UserName']
        except :
            username_list =[]
        
        if username_list == [] :
            friend_list = self.get_friend_list()
        else :
            friend_list = self.session_info_dict['friend_list']

        friend_dict = {}
        try :
            nickname_list = friend_list['NickName'][1:]
            alias_list = friend_list['Alias'][1:]
            username_list = friend_list['UserName'][1:]
            sex_list = friend_list['Sex'][1:]
            remarkname_list = friend_list['RemarkName'][1:]
        except :
            return friend_dict
        
        regex = r'<span(.*)></span>'
        rereobj = re.compile(regex)  
        
        # 系统账号
        for i in range(len(username_list)) :
            username = username_list[i]
            if not re.search('@' , username) and username == 'filehelper' :
                friend_dict[username] = '自己'

        for i in range(len(username_list)) :
            username = username_list[i]
            if username == self.session_info_dict['myself']['UserName'] :
                continue
            
            alias = alias_list[i]
            nickname = nickname_list[i]
            
            # 昵称去掉图片等字符
            nickname = rereobj.subn('', nickname)[0]
            nickname = nickname.replace(r'  ' , '')
            
            sex = sex_list[i]
            remarkname = remarkname_list[i]
            if nickname == remarkname :
                remarkname = ''
            
            if sex != 0 and (re.search('@' , username) and not re.search('@@' , username)):
                if alias == '' or not alias :
                    if remarkname == '' or not remarkname :
                        friend_dict[username] = '好友--昵称：' + nickname
                    else :
                        friend_dict[username] = '好友--昵称：' + nickname + '--备注：' + remarkname
                else :
                    if remarkname == '' or not remarkname :
                        friend_dict[username] = '好友--昵称：' + nickname + '--微信号：' + alias
                    else :
                        friend_dict[username] = '好友--昵称：' + nickname + '--备注：' + remarkname + '--微信号：' + alias

        for i in range(len(username_list)) :
            username = username_list[i]
            if username == self.session_info_dict['myself']['UserName'] :
                continue
            alias = alias_list[i]
            nickname = nickname_list[i]
            
            # 昵称去掉图片等字符
            nickname = rereobj.subn('', nickname)[0]
            nickname = nickname.replace(r'  ' , '')
            
            sex = sex_list[i]
            remarkname = remarkname_list[i]
            if nickname == remarkname :
                remarkname = ''
            
            if sex == 0 and (re.search('@' , username) and not re.search('@@' , username)):
                # 公众号或者没有设置性别的好友
                if len(username) >= 50 and alias != 'weixingongzhong':
                    if alias == '' or not alias :
                        if remarkname == '' or not remarkname :
                            friend_dict[username] = '疑似好友--昵称：' + nickname
                        else :
                            friend_dict[username] = '疑似好友--昵称：' + nickname + '--备注：' + remarkname
                    else :
                        if remarkname == '' or not remarkname :
                            friend_dict[username] = '疑似好友--昵称：' + nickname + '--微信号：' + alias
                        else :
                            friend_dict[username] = '疑似好友--昵称：' + nickname + '--备注：' + remarkname + '--微信号：' + alias

        for i in range(len(username_list)) :
            username = username_list[i]
            nickname = nickname_list[i]

            if re.search('@@' , username):
                friend_dict[username] = '群--' + '昵称:' + nickname
        
        self.session_info_dict['friend_list'] = friend_list
        self.session_info_dict['friend_dict'] = friend_dict
        return self.session_info_dict
