import json, os, time

class Manage_Logininfo():
    def __init__(self):
        self.dir = '/dev/shm/lykchat/'
        if os.path.exists(self.dir) :
            if not os.path.isdir(self.dir)  :
                os.rename(self.dir, self.dir + '-' + str(int(time.time)) + '-lykchat-bk')
                os.mkdir(self.dir)
        else :
            os.mkdir(self.dir)


    def update(self, info_dict):
        username = info_dict['username']
        user_file = self.dir + username
        info_dict['change_timestamp'] = int(time.time())
        info = json.dumps(info_dict)
        status = info_dict['status']
        status = int(status)
        if status >= 400 :
            os.remove(user_file)
        else :
            open(user_file, 'w').write(info)
            
        self._clear_expire()
        
        
    def _clear_expire(self):
        '''
        清理过期回话信息
        '''
        from django.contrib.sessions.models import Session
        import datetime
        online_sessions = Session.objects.filter(expire_date__lte=datetime.datetime.now())
        
        for session in online_sessions :
            try :
                Session.objects.get(session_key=session).delete() 
                # 删除回话
            except:
                pass
        

    def get_info(self, username):
        '''
        获取微信登陆信息
        '''
        user_file = self.dir + username
        try :
            info_dict = open(user_file).read()
            info_dict = json.loads(info_dict)
        except :
            info_dict = {}


        try : 
            status = info_dict['status']
            if status :
                status = int(status)
            else :
                status = 100
        except :
            status = 100
        
        if status == 100 :
            info_dict = {
                'uuid' : '',
                'status' : 100,
                'redirect_uri' : '',
                'login_info' :{},
                'web_request_base_dict' : {},
                'login_stamptime' : 0,
                'qr_stamptime' : 0,
                'nickname':'',
                'alias':'',
                'qr_url':'',
                'friend_dict' : {},
                'friend_list':{},
                'frienduser_list':[],
                'groupuser_list':[],
                'myself':[],
            }

        return info_dict


    def get_history_all(self):
        '''
        获取所有用户信息
        '''
        all_info_dict = {}
        for username in os.listdir(self.dir) :
            user_file = self.dir + username
            info_dict = open(user_file).read()
            info_dict = json.loads(info_dict)
            all_info_dict[username] = info_dict
            
        return all_info_dict
        
