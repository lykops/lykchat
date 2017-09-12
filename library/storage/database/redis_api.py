'''
参考文献https://pypi.python.org/pypi/redis/2.10.5
redis模块可实现redis的单机版、sentinel模式，支持Publish/Subscribe、pineline、线程等功能
'''

import pickle, redis, logging


from library.config.database import redis_config
from library.utils.type_conv import bytes2string

class Op_Redis():
    '''
    连接并操作redis
    '''
    def __init__(self, dest=None):
        self.logger = logging.getLogger("database")
        
        config = redis_config
        if dest is None :
            dest_conf = config['default']
        else :
            dest_conf = config[dest]
            
        host = dest_conf['host']
        port = dest_conf['port']
        db_name = dest_conf['db']
        try :
            db_name = dest_conf['db']
        except :
            db_name = 0
        
        pwd = dest_conf['pwd']
        try :
            pwd = dest_conf['pwd']
        except :
            pwd = None
        
        try :
            max_connections = dest_conf['max_connections']
        except :
            max_connections = 10
        # optype = redis_config['default']['type']
        socket_timeout = config['socket_timeout']
        socket_connect_timeout = config['socket_connect_timeout']
        socket_keepalive = config['socket_keepalive']
        
        self.log_prefix = 'Redis服务器' + host + ':' + str(port) + '/' + str(db_name)

        pool = redis.ConnectionPool(host=host, port=port, db=db_name, max_connections=max_connections, password=pwd, socket_timeout=socket_timeout, socket_connect_timeout=socket_connect_timeout, socket_keepalive=socket_keepalive)
        self.connecter = redis.Redis(connection_pool=pool)
     
     
    def _single_get(self, name):
        '''
        通过_single_get()获取指定name列表或者单个name的value
        '''
        try :
            result = self.connecter.get(name)
            if result != None :
                result = bytes2string(result)
                self.logger.info(self.log_prefix + ' 查询key为' + name + '的value成功')
            else:
                self.logger.warn(self.log_prefix + ' 没有查询到key为' + name + '的数据')
        except Exception as e :
            if str(e) == "invalid password" :
                self.logger.error(self.log_prefix + ' 查询key为' + name + '的数据失败，原因：连接失败，密码错误')
                return (False, '连接失败，密码错误')
            else :
                self.logger.error(self.log_prefix + ' 查询key为' + name + '的数据失败，原因：' + str(e))
                return (False, '查询失败，' + str(e))
        
        return (True, result)
    
    
    def get(self, name, fmt='str'):
        '''
        通过get()获取指定name列表或者单个name的value
        '''
        try :
            result = self.connecter.get(name)
            self.logger.info(self.log_prefix + ' 查询key为' + str(name) + '的value成功')
            if fmt == 'str' :
                result = bytes2string(result)
            elif fmt == 'obj' :
                result = pickle.loads(result)
        except Exception as e :
            if str(e) == "invalid password" :
                self.logger.error(self.log_prefix + ' 查询key为' + str(name) + '的数据失败，原因：连接失败，密码错误')
                return (False, '连接失败，密码错误')
            else :
                self.logger.error(self.log_prefix + ' 查询key为' + str(name) + '的数据失败，原因：' + str(e))
                return (False, '查询失败，' + str(e))
        
        return (True, result)
    
    
    def scan(self):
        '''
        通过redis().scan()，获取所有key列表
        '''
        try :
            name_list = self.connecter.scan()
            self.logger.info(self.log_prefix + ' 扫描成功')
        except Exception as e :
            if str(e) == "invalid password" :
                self.logger.error(self.log_prefix + ' 扫描失败，原因：连接失败，密码错误')
                return (False, '连接失败，密码错误')
            else :
                self.logger.error(self.log_prefix + ' 扫描失败，原因：' + str(e))
                return (False, '获取所有数据失败，' + str(e))
        
        name_list = name_list[1]
        temp_list = []
        for temp in name_list :
            temp = bytes2string(temp)
            temp_list.append(temp)
        name_list = temp_list
        return (True, name_list)
    
    
    def get_all(self):
        '''
        通过scan()获取所有key的value
        '''
        result = self.scan()
        name_list = result[1]
        if not result[0] :
            self.logger.error(self.log_prefix + ' 获取所有数据失败，原因：' + str(name_list))
            return (False, name_list)
        
        self.logger.info(self.log_prefix + ' 获取所有数据成功')
        return self.mget(name_list)
    
        
    def _single_del(self, name):
        
        '''
        通过redis().delete()删除指定单个name
        '''
        name = bytes2string(name)
                
        try :
            result = self.connecter.delete(name)
            self.logger.info(self.log_prefix + ' 删除key为' + name + '执行成功')
        except Exception as e :
            if str(e) == "invalid password" :
                self.logger.error(self.log_prefix + ' 删除key为' + name + '失败，原因：连接失败，密码错误')
                return (False, '连接失败，密码错误')
            else :
                self.logger.error(self.log_prefix + ' 删除key为' + name + '失败，原因：' + str(e))
                return (False, '删除失败，' + str(e))

        return (True, result)
        
        
    def delete(self, name):
        '''
        通过_single_del()删除指定单个name或者name列表
        '''
        result_list = []
        if isinstance(name, (list, tuple)) :
            for n in name :
                n = bytes2string(n)
                
                result = self._single_del(n)[1]
                result_list.append(result)
        else :
            result_list = [self._single_del(name)[1]]
            
        return result_list
    
    
    def set(self, set_dict, fmt='str') :
        
        '''
        通过redis().set()设置指定单个name或者name列表
        '''
        
        try :
            if 'name' in set_dict :
                name = set_dict['name']
                if name == '' or not name :
                    self.logger.error(self.log_prefix + ' 修改数据，原因：参数set_dict缺少key名')
                    return (False, '修改数据，参数set_dict缺少key名')
            else :
                self.logger.error(self.log_prefix + ' 修改数据，原因：参数set_dict缺少key名')
                return (False, '修改数据，参数set_dict缺少key名')
                
            if 'value' in set_dict :
                value = set_dict['value']
            else :
                value = None

            if 'ex' in set_dict :
                ex = set_dict['ex']
                try :
                    ex = int(ex)
                except :
                    ex = None
            else :
                ex = None
            # ex不能设置太长的
                    
            if ex == None or not ex:
                if 'px' in set_dict :
                    px = set_dict['px']
                    try :
                        px = int(px)
                    except :
                        px = None
                else :
                    px = None
            else :
                px = None
                    
            if 'nx' in set_dict :
                nx = set_dict['nx']
            else :
                nx = False
                    
            if 'xx' in set_dict :
                xx = set_dict['xx']
            else :
                xx = False
                    
            if fmt == 'obj' :
                result = self.connecter.set(name, pickle.dumps(value), ex=ex, px=px, nx=nx, xx=xx)
            else :
                result = self.connecter.set(name, value, ex=ex, px=px, nx=nx, xx=xx)
        except Exception as e:
            if str(e) == "invalid password" :
                self.logger.error(self.log_prefix + ' 修改/设置key为' + name + '失败，原因：连接失败，密码错误')
                return (False, '连接失败，密码错误')
            else :
                self.logger.error(self.log_prefix + ' 修改/设置key为' + name + '失败，原因：' + str(e))
                return (False, '修改/设置key为' + name + '失败，原因：' + str(e))
        
        self.logger.info(self.log_prefix + ' 修改/设置key为' + name + '执行成功')
        return (True, result)
    
    
    def _single_getset(self, name):
        
        '''
        通过redis().getset()获取或者指定指定单个name的value
        '''
        
        def kv(k, v):
            k = bytes2string(k)
            try :
                result = self.connecter.getset(k, v)
                if not result :
                    result = v
            except Exception as e :
                if str(e) == "invalid password" :
                    self.logger.error(self.log_prefix + ' 获取key（如果不存在，写入新的）为' + k + '失败，原因：连接失败，密码错误')
                    return (False, '连接失败，密码错误')
                else :
                    self.logger.error(self.log_prefix + ' 获取key（如果不存在，写入新的）为' + k + '失败，原因：' + str(e))
                    return (False, '获取key（如果不存在，写入新的）失败，' + str(e))
            
            result = bytes2string(result)
            self.logger.error(self.log_prefix + ' 获取key（如果不存在，写入新的）为' + k + '成功')
            return (True, result)
        
        if isinstance(name, (list, tuple)):
            (k, v) = name
            result = kv(k, v)[1]
        elif isinstance(name, dict):
            (k, v) = [[key, name[key]] for key in name][0]
            result = kv(k, v)[1]
        else :
            result = self._single_get(name)[1]
            k = name
            
        return (k, result)
    
    
    def getset(self,name):
        '''
        批量设置或者获取name值
        '''
        result_list = []
        result_dict = {}
        if isinstance(name, (list, tuple)) :
            for n in name :
                (key, result) = self._single_getset(n)
                result_list.append(result)
                result_dict[key] = result
        else :
            (key, result) = self._single_getset(name)
            result_list = [result]
            result_dict[key] = result
            
        return result_dict
     
     
    def mset(self, set_dict):
        '''
        批量设置
        '''
        try :
            result = self.connecter.mset(set_dict)
        except Exception as e :
            if str(e) == "invalid password" :
                self.logger.error(self.log_prefix + ' 批量修改/设置失败，原因：连接失败，密码错误')
                return (False, '连接失败，密码错误')
            else :
                self.logger.error(self.log_prefix + ' 批量修改/设置失败，原因：' + str(e))
                return (False, '批量修改/设置，' + str(e))
            
        self.logger.info(self.log_prefix + ' 批量修改/设置成功')
        return (True, result)
  
  
    def mget(self, key_list):
        '''
        批量获取
        '''

        try :
            result = self.connecter.mget(key_list)
        except Exception as e :
            if str(e) == "invalid password" :
                self.logger.error(self.log_prefix + ' 批量查询失败，原因：连接失败，密码错误')
                return (False, '连接失败，密码错误')
            else :
                self.logger.error(self.log_prefix + ' 批量查询失败，原因：' + str(e))
                return (False, '批量查询，' + str(e))
        
        result_list = []
        for r in result :
            if r != None :
                r = bytes2string(r)
                
            result_list.append(r)
        
        self.logger.info(self.log_prefix + ' 批量查询成功')
        return (True, result_list)
  

    def haskey(self, name):
        try :
            result = self.connecter.keys(name)
            self.logger.error(self.log_prefix + ' 查询key是否存在成功')
            if result :
                return True
            else :
                return False
        except Exception as e :
            if str(e) == "invalid password" :
                self.logger.error(self.log_prefix + ' 查询key是否存在失败，原因：连接失败，密码错误')
                return (False, '连接失败，密码错误')
            else :
                self.logger.error(self.log_prefix + ' 查询key是否存在失败，原因：' + str(e))
                return (False, '查询key是否存在失败，' + str(e))
            

    def getkey(self, name=None):
        
        '''
        获取key列表
        :parm
            name：查询key，模糊查询，需要在key中预先写好*
        '''
        
        try :
            if name is None :
                result = self.connecter.keys()
            else :
                result = self.connecter.keys(pattern=name)
            self.logger.error(self.log_prefix + ' 查询所有key是否存在成功')
            return (True, result)
        except Exception as e :
            if str(e) == "invalid password" :
                self.logger.error(self.log_prefix + ' 查询key是否存在失败，原因：连接失败，密码错误')
                return (False, '连接失败，密码错误')
            else :
                self.logger.error(self.log_prefix + ' 查询key是否存在失败，原因：' + str(e))
                return (False, '查询key是否存在失败，' + str(e))
