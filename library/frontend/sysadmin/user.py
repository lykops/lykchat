import time

from library.config.frontend import adminuser
from library.frontend import Base
from library.utils.time_conv import timestamp2datetime


class Manager_User(Base):
    
    def is_has(self, username):
        
        '''
        查看用户是否存在
        '''
        
        result = self.mongoclient.find(self.userinfo_mongocollect, condition_dict={'username':username})
        if not result[0] or (result[1] is None or not result[1]) :
            return False
        else :
            return True 
        
    
    def summary(self):
        
        '''
        用户列表
        '''
        
        result = self.get_userinfo()
        get_field = ['username', 'name', 'isalive' , 'lastlogin_time']
        if not result :
            self.logger.info('查询失败或者没有用户，原因：' + str(result[1]))
            return (False, result[1])
        else :
            query_list = []
            for data in result:
                temp_list = []
                
                if 'lastlogin_time' not in data :
                    data['lastlogin_time'] = ''
                
                for key, vaule in data.items() :
                    if key == 'lastlogin_time' :
                        vaule = timestamp2datetime(vaule)
                        if not vaule :
                            vaule = '-'

                    if key == 'isalive' :
                        if vaule :
                            vaule = '是'
                        else :
                            vaule = '否'
                            
                    if key in get_field :
                        temp_list.append(vaule)
            
                query_list.append(temp_list)    
            
            return (True, query_list)
        
    
    def isalive(self,username):
        userinfo = self.get_userinfo(username=username)
        if not userinfo :
            content = '用户' + username + '不存在'
            self.logger.error(content)
            return (False, content)
        else :
            try :
                isalive = userinfo['isalive']
                if not isalive :
                    content = '用户' + username + '已被禁止登陆'
                    self.logger.warn(content)
                    return (False, content)
                else :
                    return (True,userinfo)
            except :
                content = '用户' + username + '不存在'
                self.logger.error(content)
                return (False, content)
        

    def login(self, username, password):
        
        '''
        用户登陆
        '''
        
        result = self.isalive(username)
        if not result[0] :
            return result
        user_dict = result[1]
        cipher_pwd = user_dict['password']
        
        result = self.password_api.verify(password, cipher_pwd)
        if not result :
            self.logger.error('用户' + username + '登陆失败，原因：输入的登陆密码不正确')
            return (False, '输入的登陆密码不正确')
        
        update_dict = {'collect':self.userinfo_mongocollect, 'data':{"$set": {'lastlogin_time':time.time()}}}
        self.mongoclient.update({'username':username}, update_dict, addtime=True)
        self.redisclient.delete(self.userinfo_rediskey)
        return (True, '登录成功')
    

    def disable(self, username, editer=False):
        
        '''
        禁用用户
        '''
        
        userinfo = self.get_userinfo(username=username)
        if not userinfo :
            content = '禁用用户' + username + '失败，原因：用户不存在'
            self.logger.error(content)
            return (False, content)
        
        if username == adminuser :
            self.logger.warn('禁用用户' + username + '失败，原因：该用户是超级管理员，不能被禁用')
            return (False, '该用户是超级管理员，不能被禁用')
        
        if editer and editer == username :
            self.logger.warn('禁用用户' + username + '失败，原因：该用户是当前登陆者（即自己不能禁用自己），不能被禁用')
            return (False, '该用户是当前登陆者（即自己不能禁用自己），不能被禁用')
        
        if not editer :
            editer = username

        update_dict = {
            'collect':self.userinfo_mongocollect,
            'data':{
                "$set": {
                    'lastediter' : editer,
                    'lastedit_time' : time.time(),
                    'isalive':False,
                    }
                }
            }
        result = self.mongoclient.update({'username':username}, update_dict, addtime=True)
        self.redisclient.delete(self.userinfo_rediskey)
        if result[0] :
            content = '用户' + username + '禁用成功'
            self.logger.info(content)
            return (True, content)
        else :
            self.logger.error('用户' + username + '禁用失败，原因：' + result[1])
            return (False, result[1])
        
        
    def enable(self, username, editer=False):
        
        '''
        启用用户
        '''
        
        userinfo = self.get_userinfo(username=username)
        if not userinfo :
            self.logger.error('激活用户' + username + '失败，原因：用户不存在')
            return (False, '用户不存在')
        
        if not editer :
            editer = username

        update_dict = {
            'collect':self.userinfo_mongocollect,
            'data':{
                "$set": {
                    'lastediter' : editer,
                    'lastedit_time' : time.time(),
                    'isalive':True,
                    }
                }
            }
        result = self.mongoclient.update({'username':username}, update_dict, addtime=True)
        self.redisclient.delete(self.userinfo_rediskey)
        if result[0] :
            content = '用户' + username + '激活成功'
            self.logger.info(content)
            return (True, content)
        else :
            self.logger.error('用户' + username + '激活失败，原因：' + result[1])
            return (False, result[1])
        

    def edit(self, user_mess_dict):
        
        '''
        编辑用户信息
        '''
        
        set_dict = {}

        if isinstance(user_mess_dict, dict) and not user_mess_dict :
            self.logger.error('编辑用户基本信息失败，原因：参数user_mess_dict不是一个非空字典')
            return (False, '参数user_mess_dict不是一个非空字典')

        if 'username' not in user_mess_dict :
            self.logger.error('编辑用户基本信息失败，原因：参数user_mess_dict不包含username')
            return (False, '参数user_mess_dict不包含username')
        
        username = user_mess_dict['username']
        condition_dict = {'username' : username}
            
        old_user_dict = self.get_userinfo(username=username)
        if not old_user_dict :
            self.logger.error('编辑用户' + username + '基本信息失败，原因：用户不存在')
            return (False, '用户不存在')

        if 'isalive' in user_mess_dict and user_mess_dict['isalive']:
            if 'isalive' in old_user_dict :
                if user_mess_dict['isalive'] != old_user_dict['isalive'] :
                    set_dict['isalive'] = user_mess_dict['isalive']
            else :
                set_dict['isalive'] = user_mess_dict['isalive']
                
        if 'contact' in user_mess_dict and user_mess_dict['contact'] :
            if 'contact' in old_user_dict :
                if user_mess_dict['contact'] != old_user_dict['contact'] :
                    set_dict['contact'] = user_mess_dict['contact']
            else :
                set_dict['contact'] = user_mess_dict['contact']
                
        if 'name' in user_mess_dict and user_mess_dict['name']:
            if 'name' in old_user_dict :
                if user_mess_dict['name'] != old_user_dict['name'] :
                    set_dict['name'] = user_mess_dict['name']
            else :
                set_dict['name'] = user_mess_dict['name']
                
        if 'ifpwd' in user_mess_dict and user_mess_dict['ifpwd']:
            if 'ifpwd' in old_user_dict :
                if user_mess_dict['ifpwd'] != old_user_dict['ifpwd'] :
                    set_dict['ifpwd'] = user_mess_dict['ifpwd']
            else :
                set_dict['ifpwd'] = user_mess_dict['ifpwd']
                
        if not set_dict :
            self.logger.warn('编辑用户' + username + '用户基本信息失败，原因：没有任何数据需要更新')
            return (False, '没有任何数据需要更新')
        
        set_dict['lastedit_time'] = time.time()
        set_dict['lastediter'] = user_mess_dict['lastediter']
        
        update_dict = {'collect':self.userinfo_mongocollect, 'data':{"$set": set_dict}}
        result = self.mongoclient.update(condition_dict, update_dict, addtime=True)
        self.redisclient.delete(self.userinfo_rediskey)
        if result[0] :
            content = '编辑用户' + username + '基本信息成功'
            self.logger.info(content)
            return (True, content)
        else :
            self.logger.info('编辑用户' + username + '基本信息失败，原因：' + result[1])
            return (False, result[1])


    def change_pwd(self, user_mess_dict):
        
        '''
        修改用户登陆密码
        '''
        
        set_dict = {}
        if isinstance(user_mess_dict, dict) and not user_mess_dict :
            self.logger.error('修改用户登陆密码失败，原因：参数user_mess_dict不是一个非空字典')
            return (False, '参数user_mess_dict不是一个非空字典')

        if 'username' not in user_mess_dict :
            self.logger.error('修改用户登陆密码失败，原因：参数user_mess_dict不包含username')
            return (False, '参数user_mess_dict不包含username')
        
        username = user_mess_dict['username']
        condition_dict = {'username' : username}
            
        old_user_dict = self.get_userinfo(username=username)
        if not old_user_dict :
            self.logger.error('修改用户' + username + '登陆密码失败，原因：用户不存在')
            return (False, '用户不存在')
            
        password = user_mess_dict['password']
        passwordconfirm = user_mess_dict['password-confirm']

        if (password and not passwordconfirm) or (not password and passwordconfirm) or password != passwordconfirm:
            self.logger.error('修改用户' + username + '登陆密码失败，原因：两次输入的登陆密码不一致')
            return (False, '两次输入的登陆密码不一致')

        if password and passwordconfirm:
            result = self.password_api.encryt(password)
            if not result[0] :
                self.logger.error('修改用户' + username + '登陆密码失败，原因：无法加密登陆密码，' + result[1])
                return (False, '无法加密登陆密码，' + result[1])
                    
            if old_user_dict['password'] != result[1] :
                set_dict['password'] = result[1]
                
        if not set_dict :
            self.logger.warn('修改用户' + username + '登陆密码失败，原因：没有任何数据需要更新')
            return (False, '没有任何数据需要更新')
        
        set_dict['lastedit_time'] = time.time()
        set_dict['lastediter'] = user_mess_dict['lastediter']
        
        update_dict = {'collect':self.userinfo_mongocollect, 'data':{"$set": set_dict}}
        result = self.mongoclient.update(condition_dict, update_dict, addtime=True)
        self.redisclient.delete(self.userinfo_rediskey)
        if result[0] :
            content = '修改用户' + username + '登陆密码成功'
            self.logger.info(content)
            return (True, content)
        else :
            self.logger.info('修改用户' + username + '登陆密码失败，原因：' + result[1])
            return (False, result[1])

 
    def create(self, user_mess_dict):
        
        '''
        创建用户
        '''
        
        if isinstance(user_mess_dict, dict) and not user_mess_dict :
            self.logger.error('创建用户失败，原因：参数user_mess_dict不是一个非空字典')
            return (False, '参数user_mess_dict不是一个非空字典')

        if 'username' in user_mess_dict :
            username = user_mess_dict['username']
        else :
            self.logger.error('创建用户失败，原因：参数user_mess_dict不包含username')
            return (False, '参数user_mess_dict不包含username')
            
        old_user_dict = self.get_userinfo(username=username)
        if old_user_dict :
            self.logger.error('创建用户' + username + '失败，原因：用户已存在')
            return (False, '用户' + username + '已存在')
            
        if 'password' in user_mess_dict :
            password = user_mess_dict['password']
        else :     
            self.logger.error('创建用户' + username + '失败，原因：请输入用户的登陆密码')
            return (False, '请输入用户密码')
        
        if 'password-confirm' in user_mess_dict :
            passwordconfirm = user_mess_dict['password-confirm']
        else :
            self.logger.error('创建用户' + username + '失败，原因：请输入用户的登陆密码')
            return (False, '请输入用户密码')

        if 'ifpwd' in user_mess_dict :
            ifpwd = user_mess_dict['ifpwd']
        else :
            self.logger.error('创建用户' + username + '失败，原因：请输入用户的interface密码')
            return (False, '请输入用户的interface密码')

        if password != passwordconfirm :  
            self.logger.error('创建用户' + username + '失败，原因：两次输入的登陆密码不一致')
            return (False, '两次输入的登陆密码不一致')
        
        if password == ifpwd :  
            self.logger.error('创建用户' + username + '失败，原因：登陆密码和接口密码相同')
            return (False, '登陆密码和接口密码相同')
        
        result = self.password_api.encryt(password)
        if not result[0] :
            self.logger.error('创建用户' + username + '失败，原因：无法加密登陆密码' + result[1])
            return (False, '无法加密登陆密码' + result[1])
        cipher_lpwd = result[1]

        insert_data = {
            'username' : username,
            'name' : user_mess_dict['name'],
            'contact' : user_mess_dict['contact'],
            'ifpwd' : ifpwd,
            'password': cipher_lpwd,
            'isalive': True,
            'create_time': time.time(),
            'creater' : user_mess_dict['creater'],
            }

        insert_dict = {
            'collect' : self.userinfo_mongocollect,
            'data' : insert_data
            }
        
        result = self.mongoclient.insert(insert_dict, addtime=True)
        self.redisclient.delete(self.userinfo_rediskey)        
        if not result[0] :
            self.logger.error('创建用户' + username + '失败，原因：' + result[1])
        else :
            self.logger.info('创建用户' + username + '成功')
        return result


    def detail(self, username):
        
        '''
        查看用户详细信息
        '''
        
        old_user_dict = self.get_userinfo(username=username)
        if not old_user_dict :
            self.logger.error('查看用户' + username + '详细信息失败，原因：用户不存在')
            return (False, '用户' + username + '不存在')
        
        result = self.mongoclient.find(self.userinfo_mongocollect, condition_dict={'username':username})
        if not result[0] :
            self.logger.error('查看用户' + username + '详细信息失败，原因：' + str(result[1]))
            return (False, '查询用户失败，' + str(result[1]))
        
        detail_mess = result[1][0]
        if detail_mess['isalive'] :
            isalive = '是'
        else :
            isalive = '否'
        
        if 'create_time' in detail_mess:
            create_date = timestamp2datetime(detail_mess['create_time'])
        else:
            create_date = timestamp2datetime(detail_mess['add_time'])
        
        if 'lastlogin_time' in detail_mess :
            lastlogin_time = timestamp2datetime(detail_mess['lastlogin_time'])
        else :
            lastlogin_time = '-'
        
        if 'lastedit_time' in detail_mess :
            lastedit_time = timestamp2datetime(detail_mess['lastedit_time'])
        else :
            lastedit_time = '-'

        if 'creater' in detail_mess :
            creater = detail_mess['creater']
        else :
            creater = '-'
        
        if 'lastediter' in detail_mess :
            lastediter = detail_mess['lastediter']
        else :
            lastediter = '-'
        
        detail_dict = {
            '真实姓名' : detail_mess['name'],
            '联系方式' : detail_mess['contact'],
            '接口密码' : detail_mess['ifpwd'],
            '是否激活' : isalive,
            '创建者' : creater,
            '创建时间' : create_date,
            '上次登录时间' : lastlogin_time,
            '上次编辑用户' : lastediter,
            '上次编辑时间' : lastedit_time,
            '是否激活' : isalive,
            }

        self.logger.info('查看用户' + username + '详细信息成功')
        return (True, detail_dict)

