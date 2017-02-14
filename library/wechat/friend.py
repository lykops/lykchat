import json, time, re

from library.config import wechat
from library.visit_url.request.session import Request_Url


class Get_Friend():
    def __init__(self , login_info, web_request_base_dict, friend_list={}):
        self.login_info = login_info
        self.web_request_base_dict = web_request_base_dict
        self.emoji_regex = r'<span class="emoji emoji(.{1,10})"></span>'
        self.base_url = self.login_info['url']
        self.base_request = self.login_info['BaseRequest']
        self.pass_ticket = login_info['pass_ticket']
        self.skey = self.login_info['skey']
        self.firstpage_contactlist = self.login_info['firstpage_contactlist']
        '''
        self.sid = self.login_info['wxsid']
        self.uin = self.login_info['wxuin']
        self.deviceid = self.login_info['deviceid']
        self.sync_url = self.login_info['sync_url']
        '''
        
        self.field_list = wechat.friendlist_field_list

        if friend_list == {} :
            for field in self.field_list:
                friend_list[field] = []

        self.friend_list = friend_list
        
        
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
        url = '%s/webwxgetcontact?r=%s&seq=0&skey=%s' % (self.base_url, int(time.time()), self.skey)
        open_url = Request_Url(url, **self.web_request_base_dict)
        url_req = open_url.return_context()
    
        member_list = json.loads(url_req.content.decode('utf-8', 'replace'))['MemberList']
        '''
            [{'RemarkPYQuanPin': '', 'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=645115088&username=@4f9f900c9207f0d6d1e104ed99561de1&skey=@crypt_2b05caf0_8cef13f418418c2333f2cb1a3b3172e1', 'AppAccountFlag': 0, 'Statues': 0, 'SnsFlag': 0, 'AttrStatus': 0, 'PYQuanPin': 'gaoxiaokaifayunwei', 'City': 'Chaoyang', 'HideInputBarFlag': 0, 'ContactFlag': 3, 'Uin': 0, 'Sex': 0, 'PYInitial': 'GXKFYW', 'OwnerUin': 0, 'RemarkName': '', 'Alias': 'DevOpsGeek', 'Signature': 'InfoQ。~', 'KeyWord': 'gh_', 'RemarkPYInitial': '', 'UniFriend': 0, 'UserName': '@4f9f900c9207f0d6d1e104ed99561de1', 'ChatRoomId': 0, 'MemberCount': 0, 'Province': 'Beijing', 'DisplayName': '', 'NickName': '高效开发运维', 'VerifyFlag': 24, 'EncryChatRoomId': '', 'StarFriend': 0, 'MemberList': []}]
            sex:
                1为男
                2为女
                0为其他
        '''
     
        # self.friend_list = {}
        # 强制更新好友列表
            
        for field in self.field_list:
            self.friend_list[field] = []
        # 需要清空，否则在web页面上登陆后，不更新程序时，出现旧数据不会并删除
            
        self._update_myself()
        # 更新个人信息

        for friend_message in member_list :
            self._update_friend(friend_message)
            
        self.update_friend_list()
        # 更新群信息
        return self.friend_list


    def get_singlefriend_dict(self, friend, post_field='UserName'):
        '''
        好友信息进行转化，把现有字段post_field转化从字典
        '''        
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


    def get_friend(self, friend, post_field='UserName', get_field=''):
        '''
        好友信息进行转化，把现有字段post_field转化需要获得字段get_field
        '''
        friend_dict = self.get_singlefriend_dict(friend, post_field)
        if friend_dict == {}:
            return 'error'
        else :
            if not get_field in self.field_list :
                return friend_dict['NickName']
            else :
                return friend_dict[get_field]

    
    def update_friend_list(self):
        '''
        通过微信第一页好友列表获取好友，追加好友
        '''
        # wx_init = Login(self.web_request_base_dict, login_info=self.login_info)
        # contact_list = wx_init.get_firstpage_contactlist()
        contact_list = self.firstpage_contactlist

        for contact in contact_list :
            self._update_friend(contact)
                    
        return self.friend_list


    def get_group_contact(self, group_username , username='' , username_list=[]):
        '''
        根据群的username和成员的username，获得成员信息
        '''
        url = '%s/webwxbatchgetcontact?type=ex&r=%s&lang=en_US&pass_ticket=%s' % (self.base_url, int(time.time() * 1000), self.pass_ticket)
        post_list = []
        
        if group_username == [] or not group_username :
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
        根据群的username和成员的username，获得成员信息
        '''
        my_user = self.login_info['myself']['UserName']

        # wx_init = Login(self.web_request_base_dict, login_info=self.login_info)
        # contact_list = wx_init.get_firstpage_contactlist()
        contact_list = self.firstpage_contactlist

        for contact in contact_list :
            contact_user = contact['UserName']
            if re.search('@@' , contact_user) :
                break
        
        if contact_list == [] :
            contact_user = False
        
        if not contact_user :
            pass
        else :
            group_contact_dict = self.get_group_contact(contact_user , username=my_user)
            self.login_info['myself']['Alias'] = group_contact_dict[my_user]['Alias']

        self._update_friend(self.login_info['myself'])
        return self.login_info['myself']


    def return_friend_list(self):
        return self.friend_list


    def search_friend_dict(self, friend):
        '''
        提供好友名称，未知是'UserName' , 'NickName', 'Alias'，进行实时，返回第一个匹配的，返回一个字典
        '''
        
        for field in ['UserName' , 'NickName', 'Alias'] :
            if friend in self.friend_list[field] :
                return self.search_field_friend_dict(friend, field)
        
        return {}
    
    
    def search_field_friend_dict(self, friend, field):
        '''
        提供好友名称和field，返回第一个匹配的，返回一个字典
        '''
        if field in self.field_list :
            pass
        else :
            print(field + 'error')
            return {}
        
        if friend == '':
            print('friend error')
            return {}
        
        if friend in self.friend_list[field] :
            try :
                friend_index = self.friend_list[field].index(friend)
            except :
                try :
                    self.friend_list = self.update_friend_list()
                    friend_index = self.friend_list[field].index(friend)
                except :
                    print('Null')
                    return {}
                    
            search_dict = {}
            for field in self.field_list:
                search_dict[field] = self.friend_list[field][friend_index]
        
            return search_dict
        
    
    def search_friend_list(self, friend):
        '''
        提供好友名称，未知是'UserName' , 'NickName', 'Alias'，进行实时，返回匹配清单
        '''
        
        search_list = []
        
        for field in ['UserName' , 'NickName', 'Alias'] :
            i = 0
            for aa in self.friend_list[field] :
                if aa == friend :
                    username = self.friend_list['UserName'][i]
                    search_dict = self.search_field_friend_dict(username, 'UserName')
                    search_list.append(search_dict)
                i += 1
        return search_list


    def _update_friend(self, friend_message): 
        user = friend_message['UserName']
        if user in self.friend_list['UserName']:
            user_index = self.friend_list['UserName'].index(user)
            self.friend_list['Alias'][user_index] = friend_message['Alias']
            self.friend_list['NickName'][user_index] = friend_message['NickName']
            self.friend_list['Sex'][user_index] = friend_message['Sex']
            try :
                self.friend_list['RemarkName'][user_index] = friend_message['RemarkName']
            except :
                self.friend_list['RemarkName'][user_index] = ''
        else :
            for field in self.field_list:
                try :
                    value = friend_message[field]
                except :
                    value = ''
                self.friend_list[field].append(value)


    def get_friend_dict(self, friend_list={}):
        '''
        用于web页面展示
        '''
        if friend_list == {} or friend_list == '' or not friend_list :
            friend_list = self.get_friend_list()

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
                else :
                    continue
                    if alias == '' or not alias :
                        if remarkname == '' or not remarkname :
                            friend_dict[username] = '公众号--昵称：' + nickname
                        else :
                            friend_dict[username] = '公众号--昵称：' + nickname + '--备注：' + remarkname
                    else :
                        if remarkname == '' or not remarkname :
                            friend_dict[username] = '公众号--昵称：' + nickname + '--微信号：' + alias
                        else :
                            friend_dict[username] = '公众号--昵称：' + nickname + '--备注：' + remarkname + '--微信号：' + alias

        for i in range(len(username_list)) :
            username = username_list[i]
            nickname = nickname_list[i]

            if re.search('@@' , username):
                friend_dict[username] = '群--' + '昵称:' + nickname
        
        return friend_dict
