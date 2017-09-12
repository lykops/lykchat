import logging, time, re

from library.config import wechat
import library.config.wechat as wechat_conf
from library.frontend import Base
from library.storage.database.redis_api import Op_Redis
from library.utils.time_conv import timestamp2datetime

class Wechat_Base(Base):
    def __init__(self, username, redisclient=None):
        self.username = username
        self.logger = logging.getLogger("default")

        if redisclient is None :
            self.redisclient = Op_Redis()
        else :
            self.redisclient = redisclient
        
        super(Wechat_Base, self).__init__(redisclient=redisclient)
        
        self.rdskey_prefix = 'lykchat:' + self.username + ':wechat:session'
        self.rdskey_abs = self.rdskey_prefix + ':abs'
        self.rdskey_ftm = 'obj'

        self.curr_dir = wechat_conf.curr_dir
        self.qr_dir = wechat_conf.qr_dir
        self.login_status_code_dict = wechat_conf.login_status_code_dict
        self.max_upload_size = wechat_conf.max_upload_size
        self.friendlist_field_list = wechat_conf.friendlist_field_list
        self.friendlist_field_list = wechat_conf.friendlist_field_list
        
        
    def get_abs(self, force=False):
        '''
        if force :
            self.redisclient.delete(self.rdskey_prefix)
        
        result = self.redisclient.get(self.rdskey_abs, fmt=self.rdskey_ftm)
        if not result[0] or not result[1] :
            # 摘要字段为空时，读取所有字段
            abs_list = []
            result = self.redisclient.getkey(self.rdskey_prefix + ':*')
            if result[0] :
                rdskey_list = result[1]
            else :
                rdskey_list = []
                
            for rdskey in rdskey_list :
                self.logger.info(rdskey)
                result = self.redisclient.get(rdskey, fmt=self.rdskey_ftm)
                if result[0] :
                    session_info_dict = result[1]
                    if not session_info_dict :
                        continue
                    
                    status = session_info_dict.get('status', 100)
                    abs_dict = self.login_status_code_dict[status]
                    
                    login_stamptime = session_info_dict.get('login_stamptime', '')
                    logout_stamptime = session_info_dict.get('logout_stamptime', '')

                    if logout_stamptime :
                        abs_dict['logout_time'] = timestamp2datetime(stamp=logout_stamptime, fmt='%Y年%m月%d日 %H:%M:%S')
                    else :
                        abs_dict['logout_time'] = ''
                    
                    if login_stamptime :
                        abs_dict['login_time'] = timestamp2datetime(stamp=login_stamptime, fmt='%Y年%m月%d日 %H:%M:%S')
                    else :
                        abs_dict['login_time'] = ''
                    
                    abs_dict['uuid'] = session_info_dict['uuid']
                    abs_dict['alias'] = session_info_dict.get('alias', '')
                    abs_dict['nickname'] = session_info_dict.get('nickname', '')
                    abs_dict['start_timestamp'] = session_info_dict.get('start_timestamp', int(time.time()))
                    
                    abs_list.append(abs_dict)
                    
            # 写入缓存中
            self.redisclient.delete(self.rdskey_abs)
            set_dict = {
                'name' : self.rdskey_abs,
                'value' : abs_list,
                'ex':60 * 10
                }
            self.redisclient.set(set_dict, fmt=self.rdskey_ftm)
        else :
            abs_list = result[1]
        
        return  (True, abs_list)
        '''

        abs_list = []
        result = self.redisclient.getkey(self.rdskey_prefix + ':*')
        if result[0] :
            rdskey_list = result[1]
        else :
            rdskey_list = []
              
        rdskey_list.reverse()
        for rdskey in rdskey_list :
            abs_dict = {}
            result = self.redisclient.get(rdskey, fmt=self.rdskey_ftm)
            if result[0] :
                session_info_dict = result[1]
                if not session_info_dict :
                    continue
                    
                status = session_info_dict.get('status', 100)
                login_stamptime = session_info_dict.get('login_stamptime', '')
                logout_stamptime = session_info_dict.get('logout_stamptime', '')

                if logout_stamptime :
                    abs_dict['logout_time'] = timestamp2datetime(stamp=logout_stamptime, fmt='%Y年%m月%d日 %H:%M:%S')
                else :
                    abs_dict['logout_time'] = ''
                    
                if login_stamptime :
                    abs_dict['login_time'] = timestamp2datetime(stamp=login_stamptime, fmt='%Y年%m月%d日 %H:%M:%S')
                else :
                    abs_dict['login_time'] = ''
                    
                myself_dict = session_info_dict.get('myself', {})
                if not myself_dict :
                    myself_dict = {}
                abs_dict['alias'] = myself_dict.get('Alias', '')
                abs_dict['nickname'] = myself_dict.get('NickName', '')
                
                abs_dict['uuid'] = session_info_dict['uuid']
                abs_dict['start_timestamp'] = session_info_dict.get('start_timestamp', int(time.time()))
                abs_dict['descript'] = self.login_status_code_dict[status]['descript']
                abs_dict['suggest'] = self.login_status_code_dict[status]['suggest']
                abs_dict['status'] = status
                abs_list.append(abs_dict)

        return  (True, abs_list)
        
        
    def verify_ifpwd(self, ifpwd):
        uesrinfo_dict = self.get_userinfo(force=True, username=self.username)
        orig_ifpwd = uesrinfo_dict.get('ifpwd', '')
        if not orig_ifpwd :
            self.logger.warn(self.username + '没有设置接口密码')
            return (False, '请设置该用户的接口密码') 
        
        if orig_ifpwd != ifpwd :
            self.logger.warn(self.username + '输入的接口密码不正确')
            return (False, '接口密码')
        else :
            return (True, '')
