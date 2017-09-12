import json, time, re

from library.connecter.visit_url.cookie import Request_Url
from library.connecter.wechat import Base


class Get_Friend(Base): 
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
        
        url = '%s/webwxgetcontact?r=%s&seq=0&skey=%s' % (self.mmwebwx_url, int(time.time() * 1000), self.skey)
        # url = '%s/webwxgetcontact?lang=zh_CN&pass_ticket=%s&r=%s&seq=0&skey=%s' % (self.mmwebwx_url, self.pass_ticket, int(time.time() * 1000), self.skey)
        open_url = Request_Url(url, **self.web_request_base_dict)
        self.web_request_base_dict = self.session_info_dict['web_request_base_dict'] = open_url.return_web_request_base_dict()
        url_req = open_url.return_context()
    
        member_list = json.loads(url_req.content.decode('utf-8', 'replace'))
        member_list = member_list['MemberList']
        '''
            [{'RemarkPYQuanPin': '', 'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=645115088&username=@4f9f900c9207f0d6d1e104ed99561de1&skey=@crypt_2b05caf0_8cef13f418418c2333f2cb1a3b3172e1', 'AppAccountFlag': 0, 'Statues': 0, 'SnsFlag': 0, 'AttrStatus': 0, 'PYQuanPin': 'gaoxiaokaifayunwei', 'City': 'Chaoyang', 'HideInputBarFlag': 0, 'ContactFlag': 3, 'Uin': 0, 'Sex': 0, 'PYInitial': 'GXKFYW', 'OwnerUin': 0, 'RemarkName': '', 'Alias': 'DevOpsGeek', 'Signature': 'InfoQ。~', 'KeyWord': 'gh_', 'RemarkPYInitial': '', 'UniFriend': 0, 'UserName': '@4f9f900c9207f0d6d1e104ed99561de1', 'ChatRoomId': 0, 'MemberCount': 0, 'Province': 'Beijing', 'DisplayName': '', 'NickName': '高效开发运维', 'VerifyFlag': 24, 'EncryChatRoomId': '', 'StarFriend': 0, 'MemberList': []}]
            sex:
                1为男
                2为女
                0为其他
        '''
     
        for field in self.friendlist_field_list:
            self.friend_list[field] = []
        # 需要清空，否则在web页面上登陆后，不更新程序时，出现旧数据不会并删除
            
        for friend_message in member_list :
            self._update_friend(friend_message)
        
        for contact in self.firstpage_contactlist :
            self._update_friend(contact) 
        
        self._update_myself()
        # 更新个人信息
        
        self.session_info_dict['friend_list'] = self.friend_list
        return (True, self.session_info_dict)


    def get_singlefriend_dict(self, friend, post_field='UserName'):
        
        '''
        好友信息进行转化，把现有字段post_field转化从字典
        '''        
        
        if not self.friend_list :
            self.friend_list = self.get_friend_list()
        
        if post_field not in self.friendlist_field_list :
            self.logger.error('查找好友失败，字段' + post_field + '不在field_list中') 
            return (False, '查找好友失败，字段' + post_field + '不在field_list中')
        
        if not friend:
            self.logger.error('查找好友失败，参数friend为空') 
            return (False, '查找好友失败，参数friend为空')
        
        try :
            # self.update_friend_list()
            self.friend_list = self.session_info_dict['friend_list']
            friend_index = self.friend_list[post_field].index(friend)
        except Exception as e:
            self.logger.error('查找好友失败，未知错误，' + str(e))
            return (False, '查找好友失败，未知错误，' + str(e))
            
        friend_dict = {}
        for field in self.friendlist_field_list:
            friend_dict[field] = self.friend_list[field][friend_index]

        return (True, friend_dict)

    '''
    def update_friend_list(self):
        
        通过微信第一页好友列表获取好友，追加好友
        
        for contact in self.firstpage_contactlist :
            self._update_friend(contact) 
            
        self._update_myself()
        # 更新个人信息
            
        self.session_info_dict['friend_list'] = self.friend_list
        return (True,self.friend_list)
    '''

    def get_group_contact(self, group_username , username='' , username_list=[]):
        
        '''
        根据群的username和成员的username，获得成员信息
        '''
        
        url = '%s/webwxbatchgetcontact?type=ex&r=%s&lang=zh_CN&pass_ticket=%s' % (self.mmwebwx_url, int(time.time() * 1000), self.pass_ticket)
        post_list = []
        
        if not group_username or not re.search('^@@', group_username):
            self.logger.error('查找群组失败，参数group_username不是一个合法的群组') 
            return (False, '查找群组失败，参数group_username不是一个合法的群组')
        
        if username_list :
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
                self.logger.error('没有查到该群组的成员') 
                return (False, '没有查到该群组的成员')

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
                    
        return (True, group_contact_dict)


    def _update_myself(self):
        
        '''
        通过群获取登陆微信号的信息
        '''
        
        myself = self.session_info_dict['myself']
        my_user = myself['UserName']
        my_alias = myself['Alias']
        my_nick = myself['NickName']
        
        if not my_alias or not my_nick :
            try :
                group_username = self.groupuser_list[0]
            except  : 
                for contact in self.firstpage_contactlist :
                    if re.search('@@' , contact['UserName']) :
                        group_username = contact.get('UserName', '')
                        break
                    else :
                        group_username = ''
                        
            if not isinstance(group_username, str) :
                group_username = ''
        
            if group_username and re.search('@@' , group_username) :
                result = self.get_group_contact(group_username, username=my_user)
                if result[0] :
                    group_contact_dict = result[1].get(my_user, {})
                else :
                    group_contact_dict = {}
                
                if group_contact_dict:
                    self.logger.info(group_contact_dict)
                    self.session_info_dict['myself']['NickName'] = group_contact_dict['NickName']
                    self.session_info_dict['myself']['Alias'] = group_contact_dict['Alias']
                    self.session_info_dict['myself']['UserName'] = my_user
        # return (True,self.session_info_dict['myself'])


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
            for field in self.friendlist_field_list:
                try :
                    value = friend_dict[field]
                except :
                    value = ''
                self.friend_list[field].append(value)
                
        self.session_info_dict['friend_list'] = self.friend_list
