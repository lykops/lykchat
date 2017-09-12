import logging

from library.config.frontend import adminuser
from library.security.password import Manager_Password
from library.storage.database.mongo import Op_Mongo
from library.storage.database.redis_api import Op_Redis
from library.utils.time_conv import timestamp2datetime
from library.utils.type_conv import str2dict


class Base():
    def __init__(self, mongoclient=None, redisclient=None):
        
        '''
        这是用户管理部分的MVC中的C
        '''
        
        self.logger = logging.getLogger("default")
        self.userinfo_mongocollect = 'user.info'
        self.userinfo_rediskey = 'lykchat:userinfo'
        if mongoclient is None :
            self.mongoclient = Op_Mongo()
            self.logger.warn('无法继承，需要初始化mongodb连接')
        else :
            self.mongoclient = mongoclient
            
        if redisclient is None :
            self.redisclient = Op_Redis()
            self.logger.warn('无法继承，需要初始化redis连接')
        else :
            self.redisclient = redisclient

        self.password_api = Manager_Password()
        self.expiretime = 60 * 60 * 24
        self.rediskey_prefix = 'lykchat:'
            

    def get_userinfo(self, force=False, username=None):
        
        '''
        获取userinfo数据
        '''
        
        if force :
            self.logger.warn('强制删除用户信息缓存')
            self.redisclient.delete(self.userinfo_rediskey)
        
        result = self.redisclient.get(self.userinfo_rediskey, fmt='obj')
        if result[0] and (result[1] is not None or result[1]) :
            userinfo = result[1]
        else : 
            result = self.mongoclient.find(self.userinfo_mongocollect)
            if result[0] :
                userinfo = result[1]

                set_dict = {
                    'name' : self.userinfo_rediskey,
                    'value' : userinfo,
                    'ex':self.expiretime
                    }
                self.redisclient.set(set_dict, fmt='obj')
            else :
                userinfo = {}
            
        if username is None :
            return userinfo
        else :
            try :
                for u_dict in userinfo :
                    if username == u_dict['username'] :
                        us = u_dict
                    else :
                        continue
            except :
                us = {}
            
            try : 
                return us
            except :
                return {}
            
            
    def get_data(self, username, redis_key, mongo_collect, force=False, mongoshare=True):
        
        '''
        获取用户数据
        :parm
            username：用户名
            redis_key：redis缓存key名
            mongo_collect：mongo的集合名
            force：强制刷新
        '''
        
        if force:
            self.logger.warn('强制删除指定缓存')
            self.redisclient.delete(redis_key)
        
        result = self.redisclient.get(redis_key, fmt='obj')
        if not result[0] or (result[0] and not result[1]) :
            if mongoshare :
                result = self.mongoclient.find(mongo_collect, condition_dict={'username' : username})
            else :
                result = self.mongoclient.find(mongo_collect)

            if result[0] :
                data_dict = result[1]
                self.write_cache(redis_key, data_dict)
            else :
                self.logger.error('从数据库中查询数据失败，原因：' + result[1])
                return result
        else :
            data_dict = result[1]
                    
        try :
            del data_dict['username']
        except :
            pass
            
        return (True, data_dict)


    def write_cache(self, redis_key, data, expire=60 * 60, ftm='obj'):
        try :
            self.logger.warn('强制删除缓存')
            self.redisclient.delete(redis_key)
        except :
            pass
        
        set_dict = {
            'name' : redis_key,
            'value' : data,
            'ex':expire
            }
                
        result = self.redisclient.set(set_dict, fmt=ftm)
        if result[0] :
            content = '写缓存成功'
            # self.logger.info(content)
            return (True, content)
        else :
            self.logger.info('写缓存失败，原因：' + result[1])
            return (False, '写缓存失败，' + result[1])
