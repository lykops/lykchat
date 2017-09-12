import re, time

from library.connecter.wechat.friend import Get_Friend
from library.connecter.wechat.login import Login
from library.connecter.wechat.logout import Logout
from library.connecter.wechat.ready import Ready
from library.connecter.wechat.send import Send_Msg
from library.frontend.wechat import Wechat_Base
from library.utils.file import upload_file
from library.utils.time_conv import timestamp2datetime


class Manager_Single(Wechat_Base):
    def __init__(self, username, uuid=None, redisclient=None):  
        super(Manager_Single, self).__init__(username, redisclient=redisclient)
        self.uuid = uuid

    
    def _init_parm(self):
        new_dict = {
            'uuid' : None,
            'status' : 100,
            'redirect_uri' : '',
            'login_info' :{},
            'web_request_base_dict' : {},
            'login_stamptime' : 0,
            'qr_stamptime' : 0,
            'nickname':'',
            'alias':'',
            'qr_url':'',
            'start_timestamp' : int(time.time()),
            'friend_dict' : {},
            'friend_list':{},
            'frienduser_list':[],
            'groupuser_list':[],
            'myself':{},
        }
        
        if self.uuid is None :
            self.session_info_dict = new_dict
        else :
            self.rdskey_session = rdskey_session = self.rdskey_prefix + ':' + self.uuid
            result = self.redisclient.get(rdskey_session, fmt=self.rdskey_ftm)
            if result[0] :
                if not result[1]:
                    self.session_info_dict = new_dict
                else :
                    self.session_info_dict = result[1]
            else :
                self.session_info_dict = new_dict
                
        self.status = self.session_info_dict.get('status', 100)
        self.session_info_dict['send_result'] = ''
        # self.uuid = self.session_info_dict.get('uuid', None)
        
        
    def _get_friend_info(self):  
        
        '''
        获取登陆之后的好友等信息
        '''
        
        '''
        try :
            change_timestamp = int(self.session_info_dict['change_timestamp'])
        except :
            change_timestamp = 0
        
        self.friend_dict = self.session_info_dict['friend_dict']
        self.friend_list = self.session_info_dict['friend_list']
        change_time = int(time.time()) - change_timestamp
           
        if (self.friend_dict and self.friend_dict) or self.friend_list != {'UserName': [], 'NickName': [], 'Alias': [], 'Sex': [], 'RemarkName': []} :
            if change_time >= 3600:
                self.session_info_dict = self.friend_api.get_friend_list()
        else :
            self.session_info_dict = self.friend_api.get_friend_list()
        '''
        
        friend_api = Get_Friend(session_info_dict=self.session_info_dict)
        try :
            result = friend_api.get_friend_list()
            if result[0] :
                self.session_info_dict = result[1]
        except  :
            self.session_info_dict = result[1]
        
        friend_list = self.session_info_dict.get('friend_list', {})

        username_list = friend_list.get('UserName', [])
        if not username_list :
            friend_list = self.session_info_dict['friend_list']

        friend_dict = {}
        try :
            nickname_list = friend_list['NickName'][1:]
            alias_list = friend_list['Alias'][1:]
            username_list = friend_list['UserName'][1:]
            sex_list = friend_list['Sex'][1:]
            remarkname_list = friend_list['RemarkName'][1:]
        except :
            nickname_list = []
            alias_list = []
            username_list = []
            sex_list = []
            remarkname_list = []
        
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


    def index(self):
        if self.uuid is None :
            self.logger.info(self.username + '通过web页面检测登陆状态时，没有输入uuid')
            result = self.get_abs(force=True)
            if result[0] :
                abs_list = result[1]
            else :
                abs_list = []
                
            for uuid_info in abs_list :
                uuid = uuid_info.get('uuid', None)
                status = uuid_info.get('status', 100)
                start_timestamp = uuid_info.get('start_timestamp', int(time.time()))
                
                if status != 222 and status < 300  and int(time.time()) - start_timestamp < 60 and uuid is not None :
                    self.uuid = uuid
                    break
        # 处理之前为完成登陆的

        self._init_parm()
        old = self.session_info_dict['uuid']
        if old is None :
            if  self.uuid is not None:
                return (False, '该微信号没有登陆或者超时')
        elif isinstance(old, int) :
            if old >= 300 :
                return (False, '该微信号下线')
        
        if self.status < 200:
            '''
            初始化，获取uuid、cookies、session、二维码等等
            '''
            
            ready_api = Ready(session_info_dict=self.session_info_dict)
            result = ready_api.get_qr()
            if result[0] :
                self.session_info_dict = result[1]
            else :
                self.logger.info(result[1])
                return (False, '检查登陆失败，' + result[1])
            self.session_info_dict['start_timestamp'] = int(time.time())
        elif self.status > 200 and self.status < 222:
            self._confirm()
        elif self.status == 222:
            login_api = Login(session_info_dict=self.session_info_dict)
            result = login_api.check_login()
            if result[1] :
                self.session_info_dict = result[1]
            else :
                self.logger.info(result[1])
                return (False, '检查登陆失败，' + result[1])
        
            self._get_friend_info()
        elif self.status == 200 or self.status == 221:
            self._init()
        else :
            if self.status < 300 :
                ready_api = Ready(session_info_dict=self.session_info_dict)
                result = ready_api.get_qr()
                if result[1] :
                    self.session_info_dict = result[1]
                else :
                    self.logger.info(result[1])
                    return (False, '获取二维码失败，' + result[1])
            else :
                self.session_info_dict['logout_timestamp'] = self.session_info_dict.get('logout_timestamp', int(time.time()))
            
        self._session2write()
        # 把self.session_info_dict写到数据库中
        
        return_dict = self._return2html() 
        return (True, return_dict)


    def logout(self):
        
        '''
        用于微信退出
        '''
        
        self._init_parm()
        if self.status == 222 :
            logout_api = Logout(self.session_info_dict)
            logout_api.logout()
            self.session_info_dict['status'] = self.status = 444
            self.session_info_dict['logout_timestamp'] = self.session_info_dict.get('logout_timestamp', int(time.time()))
            self._session2write()
            return_dict = self._return2html() 
            return (True, return_dict)
        else :
            return_dict = self._return2html() 
            return (False, return_dict)


    def _confirm(self):
        '''
        检查是否扫描和确认登陆
        '''
        count = 0
        self._init_parm()
        while 1:
            ready_api = Ready(session_info_dict=self.session_info_dict)
            result = ready_api.check_status()
            if result[1] :
                self.session_info_dict = result[1]
            else :
                return (False, '检查登陆失败，' + result[1])
            status = self.session_info_dict['status']
            if (status == 200 or status >= 400) or count == 5 :
                break
            count += 1
        
        self._session2write()
            
        if status == 200 :
            self._init()

    
    def _init(self):
        '''
        确认登陆之后，进行登陆
        '''
        count = 0
        self._init_parm()
        while 1 :
            login_info = self.session_info_dict['login_info']
            login_api = Login(session_info_dict=self.session_info_dict)
            if not isinstance(login_info, dict) or not login_info:
                result = login_api.init_login()
            else :
                result = login_api.check_login()

            if result[1] :
                self.session_info_dict = result[1]
            else :
                return (False, '检查登陆失败，' + result[1])

            status = self.session_info_dict['status']
            if status == 222 or self.status >= 400 or count == 5 :
                if status == 222 :
                    self._get_friend_info()
                    self.session_info_dict['login_stamptime'] = int(time.time())
                break
            else :
                time.sleep(5)

            count += 1
            
        self._session2write()


    def _return2html(self):
        
        '''
        页面渲染
        '''
        
        status = self.session_info_dict['status']
        return_dict = self.login_status_code_dict[status]
        return_dict['login_stamptime'] = login_stamptime = self.session_info_dict.get('login_stamptime', 0)
        try :
            login_min = (int(time.time()) - int(login_stamptime)) // 60
        except :
            login_min = 0
            
        if login_min > 60 * 24 * 365 :
            login_min = 0  
            
        if login_min >= 60 * 24 :
            login_min = str(login_min // 60 // 24) + '天' + str(login_min // 60 % 24) + '小时' + str(login_min % 60) + '分钟'
        elif login_min >= 60 :
            login_min = str(login_min // 60) + '小时' + str(login_min % 60) + '分钟'
        else :
            login_min = str(login_min) + '分钟'
        return_dict['login_min'] = login_min
        return_dict['now_time'] = timestamp2datetime(fmt='%Y年%m月%d日 %H:%M:%S')
        
        if login_stamptime :
            return_dict['login_stamptime'] = timestamp2datetime(stamp=login_stamptime, fmt='%Y年%m月%d日 %H:%M:%S')
        else :
            return_dict['login_time'] = ''
            
        return_dict['logout_stamptime'] = logout_stamptime = self.session_info_dict.get('logout_stamptime', 0)
        if logout_stamptime :
            return_dict['logout_time'] = timestamp2datetime(stamp=logout_stamptime, fmt='%Y年%m月%d日 %H:%M:%S')
        else :
            return_dict['logout_time'] = ''
        
        return_dict['username'] = self.session_info_dict.get('username', '')
        return_dict['qr_url'] = self.session_info_dict['qr_url']
        return_dict['status'] = self.session_info_dict['status']
        return_dict['uuid'] = self.session_info_dict['uuid']
        
        try :
            return_dict['nickname'] = self.session_info_dict['myself']['NickName']
            return_dict['alias'] = self.session_info_dict['myself']['Alias']
        except :
            return_dict['nickname'] = ''
            return_dict['alias'] = ''
        
        return_dict['friend_dict'] = self.session_info_dict.get('friend_dict', {})
        return_dict['send_result'] = self.session_info_dict.get('send_result', '')
        return return_dict


    def check_login(self):
        
        '''
        用于接口或者计划任务进行检查登陆状态
        '''
        
        self._init_parm()
        if self.status == 222:
            login_api = Login(session_info_dict=self.session_info_dict)
            result = login_api.check_login()
            if result[0] :
                self.session_info_dict = result[1]
            else :
                self.logger.info('检测微信' + self.uuid + '登陆失败，原因' + result[1])
                return (False, False, '查询错误，原因' + result[1])
        elif self.status >= 300 :
            self.session_info_dict['logout_timestamp'] = self.session_info_dict.get('logout_timestamp', int(time.time()))

        self._session2write()
        status = self.session_info_dict.get('status', 400)
        return_dict = self._return2interface()
        if status == 222 :
            return (True, True, return_dict)
        else :
            return (True, False, return_dict)


    def _return2interface(self):
        status = self.session_info_dict.get('status', 400)
        return_dict = self.login_status_code_dict[status]
        return_dict['login_stamptime'] = login_stamptime = self.session_info_dict.get('login_stamptime', 0)
        if login_stamptime :
            return_dict['login_stamptime'] = timestamp2datetime(stamp=login_stamptime, fmt='%Y年%m月%d日 %H:%M:%S')
        else :
            return_dict['login_time'] = ''
            
        return_dict['logout_stamptime'] = logout_stamptime = self.session_info_dict.get('logout_stamptime', 0)
        if logout_stamptime :
            return_dict['logout_time'] = timestamp2datetime(stamp=logout_stamptime, fmt='%Y年%m月%d日 %H:%M:%S')
        else :
            return_dict['logout_time'] = ''
            
        return_dict['now_stamptime'] = int(time.time())
        return_dict['status'] = status
        return_dict['uuid'] = self.session_info_dict.get('uuid', None)
        return_dict['send_result'] = self.session_info_dict.get('send_result', {})
            
        try :
            return_dict['nickname'] = self.session_info_dict['myself']['NickName']
            return_dict['alias'] = self.session_info_dict['myself']['Alias']
        except :
            return_dict['nickname'] = ''
            return_dict['alias'] = ''
        return return_dict


    def _session2write(self):
        status = self.session_info_dict.get('status', 100)
        uuid = self.session_info_dict.get('uuid', None)
        self.logger.info(self.username + '检测微信号uuid为' + str(uuid) + '登陆情况，状态为' + str(status))
        '''
        if status > 299 :
            logout_timestamp = self.session_info_dict.get('logout_timestamp', int(time.time()))
            logintime = int(time.time()) - int(logout_timestamp)
            # expire = 60 * 60 * 24 - logintime
        else :
            login_stamptime = self.session_info_dict.get('login_stamptime', int(time.time()))
            logintime = int(time.time()) - int(login_stamptime)
            # expire = 60 * 60 * 24 * 20 - logintime
        '''
        
        self.session_info_dict['start_timestamp'] = self.session_info_dict.get('start_timestamp', int(time.time()))
        
        set_dict = {
            'name' : self.rdskey_prefix + ':' + str(uuid) ,
            'value' : self.session_info_dict,
            'ex' : 180,
            # 'ex':expire redis要求ex不能设置太长时间，否则报错
            # 根据使用经验，微信web端登陆时间有最大30天限制
            # 如果连续登陆30天后，微信端将强制退出，可能被微信端限制该微信号登陆
            # 为了防止出现这个问题，这里的微信登陆信息保存20天
            }
        self.redisclient.set(set_dict, fmt=self.rdskey_ftm)
        # result = self.redisclient.set(set_dict, fmt=self.rdskey_ftm)
        # self.logger.info(result)
        # 把self.session_info_dict写到数据库中


    def send_msg(self , tousername, content, caller='web' , filename='' , post_field='UserName'):
        
        '''
        发送信息，处理返回值
        '''
        
        self._init_parm()
        try :
            nickname = self.session_info_dict['myself']['NickName']
        except :
            nickname = ''
        
        return_dict = {
            'nickname': nickname,
            # 'alias': self.session_info_dict['myself']['Alias'],
            'uuid' : self.session_info_dict.get('uuid', None),
            'status' : self.session_info_dict.get('status', 400),
            'login_stamptime' : self.session_info_dict.get('login_stamptime', 0),
            }
        
        if self.status != 222 :
            # 验证登陆情况
            self.session_info_dict['send_result'] = '微信号【' + nickname + '】发送信息失败，</br>原因：该微信号在非登陆状态'
            if caller == 'web' :
                return_dict = self._return2html()
            else :
                pass
                
            self.logger.warn('用户名【' + self.username + '】，微信号【' + nickname + '】发送信息失败，原因：该微信号在非登陆状态')
            return (False, return_dict)
        
        send_api = Send_Msg(session_info_dict=self.session_info_dict)
        
        if filename :
            file_dict = {}
            result = upload_file(filename, filename=filename, max_upload_size=self.max_upload_size, chmods='400', force=True)
            if result[0] :
                filename = result[1]
            else :
                self.session_info_dict['send_result'] = '微信号【' + nickname + '】发送信息失败，</br>原因：文件上传到服务器失败，' + str(result[1])
                self.logger.warn('用户名【' + self.username + '】，微信号【' + nickname + '】发送信息失败，文件上传到服务器失败，原因：' + str(result[1]))
                if caller == 'web' :
                    return_dict = self._return2html()
                else :
                    file_dict['msg'] = '文件上传到服务器失败，原因：' + str(result[1])
                    file_dict['code'] = 4000
                    return_dict['text'] = file_dict
                return (False, return_dict)
        
            temp_dict = send_api.send(content, filename=filename, tousername=tousername, post_field=post_field)
            if temp_dict['Code'] == 0:
                file_content = '文件【' + str(filename) + '】发送成功'
                self.logger.info('用户名【' + self.username + '】，微信号【' + nickname + '】，文件【' + str(filename) + '】发送成功')
            else :
                file_content = '文件【' + str(filename) + '】发送失败，原因：' + str(temp_dict['Msg'])
                self.logger.warn('用户名【' + self.username + '】，微信号【' + nickname + '】，文件【' + str(filename) + '】发送失败，原因：' + str(result[1]))
                
            file_dict['msg'] = temp_dict['Msg']
            if temp_dict['Code'] == 0 :
                file_dict['ok'] = True
            else :
                file_dict['ok'] = False
            file_dict['filename'] = str(filename)
        else :
            file_dict = {}
            file_content = ''
            
        text_dict = {}
        temp_dict = send_api.send(content, tousername=tousername, post_field=post_field)
        friend = temp_dict.get('friend', '')
        if temp_dict['Code'] == 0:
            text_content = '文字【' + str(content) + '】发送成功'
            self.logger.info('用户名【' + self.username + '】，微信号【' + nickname + '】，好友【' + str(friend) + '】，文字【' + str(content) + '】发送成功')
            return_dict['ok'] = True
        else :
            text_content = '文字【' + str(content) + '】发送失败，原因：' + str(temp_dict['Msg'])
            self.logger.warn('用户名【' + self.username + '】，微信号【' + nickname + '】，好友【' + str(friend) + '】，文字【' + str(content) + '】发送失败，原因：' + str(temp_dict['Msg']))
            return_dict['ok'] = False
            
        if temp_dict['Code'] == 0 :
            text_dict['ok'] = True
        else :
            text_dict['ok'] = False
        text_dict['msg'] = temp_dict['Msg']
        text_dict['content'] = content
        return_dict['text'] = text_dict
        return_dict['file'] = file_dict
        return_dict['friend'] = friend
            
        if caller == 'web' : 
            content = '微信号【' + nickname + '】</br>向【' + str(friend) + '】发送信息，结果如下：</br>'
            content = content + text_content + '</br>'
            content = content + file_content
            self.session_info_dict['send_result'] = content
            send_dict = self._return2html()
        else :
            send_dict = return_dict
            
        return (True, send_dict)
