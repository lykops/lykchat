import threading
import time, os

import django

from library.config import wechat
from library.wechat.friend import Get_Friend
from library.wechat.login import Login
from library.wechat.receive import Receive_Msg

    
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lykchat.settings")
django.setup()


def cronwx_getsession():
    '''
        根据uuid获得状态为222的session，如果uuid为空，显示所有的
    '''
    from django.contrib.sessions.models import Session
    import datetime
    online_sessions = Session.objects.filter(expire_date__gte=datetime.datetime.now()) 
    # 获取未过期的sessions
        
    login_session_list = []
    for session in online_sessions :
        # 这里的session不要改名，否则报错
        history_session_info = session.get_decoded()
        uuid_list = []
    
        try :
            history_type = history_session_info['type']
            history_uuid = history_session_info['uuid']
            history_status = history_session_info['status']
            history_status = int(history_status)
            if history_type != wechat.session_type or history_status != 222 :
                break

            if (not history_uuid and history_uuid == '') or history_uuid in uuid_list:
                break
    
            login_session_list.append(history_session_info)
            uuid_list.append(history_uuid)
        except :
            pass
        
    return login_session_list


def cronwx_checklogin():
    from datetime import datetime
    print('开始执行微信检查登陆状态的计划任务! 现在时间: %s' % datetime.now())

    count = 0 
    while 1 :
        print()
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        if count == 10 :
            exit(0)
            break
        
        count += 1
        login_session_list = cronwx_getsession()
        if login_session_list == {} or not login_session_list :
            print('没有微信号登陆')
        else :
            for session_info_dict in login_session_list :
                check_login = Cronwx_Checksingle(session_info_dict)
                check_thread = threading.Thread(target=check_login.run_thread)
                check_thread.start()
            
            time.sleep(58)
            

class Cronwx_Checksingle():
    def __init__(self, session_info_dict):
        self.session_info_dict = session_info_dict
        self.login_info = session_info_dict['login_info']
        self.uuid = session_info_dict['uuid']
        self.web_request_base_dict = session_info_dict['web_request_base_dict']
        wx_friend = Get_Friend(self.login_info, self.web_request_base_dict)
        self.friend_list = wx_friend.get_friend_list()
        self.alias = self.friend_list['Alias'][0]
        self.nickname = self.friend_list['NickName'][0]
        self.login_stamptime = self.session_info_dict['login_stamptime']
        
    def run_thread(self):
        print('正在检查微信号为' + str(self.alias) + '，昵称为' + str(self.nickname) + '的登陆情况')
        checklogin_thread = threading.Thread(target=self._checklogin)
        checklogin_thread.start()
        # 检查登陆

        count = 0
        while 1 :      
            self._receive()
            time.sleep(5)
            if count == 60 / 5 - 1:
                exit(0)
                break
            count += 1    
            

    def _receive(self):
        '''
        接受单个微信号信息
        '''
        try:
            wx_receive = Receive_Msg(self.login_info, self.web_request_base_dict, self.friend_list)
            wx_receive.receive()
            # get_friend = Get_Friend(self.login_info, self.web_request_base_dict , friend_list=self.friend_list)
            # self.friend_list = get_friend.update_friend_list()
        except :
            pass


    def _checklogin(self):
        '''
        检查单个微信号信息
        '''
        try:
            login = Login(self.web_request_base_dict, login_info=self.login_info)
            check_login = login.check_login()
            login_time = (int(time.time()) - int(self.login_stamptime)) // 60
            if login_time >= 60 * 24 * 7:
                login_time = 0
            if check_login['Ret'] == 0 :
                print('登陆中，已经登陆了' + str(login_time) + '分钟')
            else :
                print('微信号被退出，保持登陆' + str(login_time) + '分钟，请重新执行程序')
                print(check_login)
                print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
                cronwx_clearsession(uuid=self.uuid)
        except :
            pass
        
        exit(0)


def cronwx_clearsession(uuid=''):
    '''
    清理过期回话信息
    '''
    from django.contrib.sessions.models import Session
    import datetime
    online_sessions = Session.objects.filter(expire_date__gte=datetime.datetime.now())
    for session in online_sessions :
        # 这里的session不要改名，否则报错
        try :
            history_session_info = session.get_decoded()
            history_uuid = history_session_info['uuid']
            if history_session_info['type'] != 'web_wechat_login':
                break 
                    
            if uuid and uuid != '' :
                if uuid != history_uuid :
                    break
            
                Session.objects.get(session_key=session).delete() 
        except Exception as e:
            print(e)


def apischeduler_wechat():
    from apscheduler.schedulers.blocking import BlockingScheduler
    scheduler = BlockingScheduler()
    scheduler.add_job(cronwx_checklogin, 'cron', second='0', minute='*', hour='*')
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown() 


def django_cron_wechat():
    pass
