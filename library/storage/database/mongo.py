'''
参考文献https://pypi.python.org/pypi/pymongo/3.4.0
mongodb官方推荐
'''

import time, logging, pymongo

from bson.objectid import ObjectId

from library.config.database import mongo_config
from library.utils.dict import dot2_, _2dot

class Op_Mongo():
    
    '''
    连接并操作mongo
    '''
    
    def __init__(self, dest=None, idletime=1000 * 60 * 60):
        
        self.logger = logging.getLogger("database")
        config = mongo_config
        if dest is None :
            dest_conf = config['default']
        else :
            dest_conf = config[dest]
        
        host = dest_conf['host']
        port = dest_conf['port']
        db_name = dest_conf['db']
        user = dest_conf['user']
        pwd = dest_conf['pwd']
        mechanism = config['mechanism']
        
        self.conn = pymongo.MongoClient(host=host , port=port, socketKeepAlive=True, maxIdleTimeMS=idletime, minPoolSize=0, maxPoolSize=64)
        # 长连接的使用必须要主机名，端口，标识符，用户名以及密码一样才行，否则会重新创建一个长连接
        # http://api.mongodb.com/python/current/api/pymongo/mongo_client.html
        # 连接mongodb服务器
            
        self.dbs = self.conn[db_name]
        # 连接数据库，或者db = self.conn.db_name

        self.log_prefix = 'MongoDB服务器' + host + ':' + str(port)
        try :
            self.connecter = self.dbs.authenticate(user, pwd, mechanism=mechanism)
            if not self.connecter :
                self.error_reason = self.log_prefix + '连接失败，原因：' + str(self.connecter)
            else :
                self.logger.info(self.log_prefix + '连接成功')
        except Exception as e:
            self.connecter = False
            conn_result = str(e)
            if conn_result == 'Authentication failed.' :
                self.error_reason = self.log_prefix + '连接失败，原因：账号或者密码错误'
            else :       
                self.error_reason = self.log_prefix + '连接失败，原因：' + conn_result
        
        
    def batch_insert(self, insert_list, addtime=True):
        '''
        同库批量插入数据
        '''
        if not self.connecter:
            self.logger.error(self.error_reason)
            return (False, self.error_reason)
        
        if not (isinstance(insert_list, (list, tuple))):
            self.logger.error(self.log_prefix + ' 批量插入数据失败，原因：参数insert_list不是列表或者元组')
            return (False, '批量插入数据失败，参数insert_list不是列表或者元组')
        
        insert_data = {}
        for insert_dict in insert_list :
            try :
                collect_name = insert_dict['collect']
                # 获取集合
            except :
                continue
                
            try :
                data = insert_dict['data']
                # 获取插入数据
                if not isinstance(data, dict):
                    continue
                    # 插入数据类型不为字典，不执行
                    
                if addtime :
                    data['add_time'] = time.time()
            except :
                continue
        
            if not collect_name in insert_data :
                insert_data[collect_name] = [data] 
            else :
                insert_data[collect_name].append(data)
        
        insert_data = dot2_(insert_data)
        result_dict = {}
        for collect_name , data in insert_data.items() :
            collection = self.dbs[collect_name]
            
            try :
                result = collection.insert_many(data)
            except Exception as e :
                self.logger.error(self.log_prefix + ' 批量插入数据到集合' + collect_name + '失败，原因：' + str(e))
                return (False, '批量插入数据失败，' + str(e))
             
            result_dict[collect_name] = result
            
        self.logger.error(self.log_prefix + ' 批量插入数据到集合' + collect_name + '成功')  
        return (True, result_dict)
            

    def insert(self, insert_dict, addtime=True):
        
        '''
        指定表插入数据
        :参数
            insert_dict：需要插入的数据
            addtime是否追插入日期
        :返回
            一个元组，(False,原因)或者(True, 结果) 
        '''
        
        if not self.connecter:
            self.logger.error(self.error_reason)
            return (False, self.error_reason)
        
        try :
            collect_name = insert_dict['collect']
            # 获取集合
        except Exception as e :
            self.logger.error(self.log_prefix + ' 插入数据失败，原因：参数insert_dict格式出错，缺少collect，即缺少集合名')
            return (False, '插入数据失败，参数insert_dict格式出错，缺少collect，即缺少集合名')
                
        try :
            data = insert_dict['data']
            # 获取插入数据
            if not isinstance(data, dict):
                self.logger.error(self.log_prefix + ' 插入数据到集合' + collect_name + '失败，原因：参数insert_dict格式出错，data值不为字典')
                return (False, '插入数据到集合' + collect_name + '失败，参数insert_dict格式出错，data值不为字典')
        except Exception as e:
            self.logger.error(self.log_prefix + ' 插入数据到集合' + collect_name + '失败，原因：参数insert_dict格式出错，缺少键data')
            return (False, '插入数据失败，参数insert_dict格式出错，缺少键data')
        
        if addtime :
            data['add_time'] = time.time()

        collection = self.dbs[collect_name]
        data = dot2_(data)
        try :
            result = collection.insert(data)
            self.logger.info(self.log_prefix + ' 插入数据到集合' + collect_name + '成功')
            return (True, result)
        except Exception as e :
            self.logger.error(self.log_prefix + ' 插入数据到集合' + collect_name + '失败，原因：' + str(e))
            return (False, '插入数据失败，' + str(e))
            

    def _handler_condition(self, condition_dict):
        '''
        在查询或更新数据时，对查询条件进行处理
        '''
        condition_dict = dot2_(condition_dict)
        for k, v in condition_dict.items() :
            if k == '_id' :
                # 把_id的值进行转化
                if isinstance(v, str) :
                    try :
                        v = int(v)
                    except :
                        v = ObjectId(v)
                                
                    condition_dict[k] = v
                
        return condition_dict


    def _handler_result(self, query_list, get_field=[]):
        '''
        在查询数据时，处理查询结果
        '''

        result_list = []
        for result_dict in query_list :
            result_dict = _2dot(result_dict)   
            
            try :
                del result_dict['traceback']
            except :
                pass
            del result_dict['_id']
            
            if not isinstance(get_field, (list, tuple)) or not get_field :
                temp_dict = result_dict
            else:
                temp_dict = {}
                for field in get_field :
                    try :
                        temp_dict[field] = result_dict[field]
                    except :
                        temp_dict[field] = 'no data'
                
            result_list.append(temp_dict)

        return result_list


    def _getresult_fielddict(self, result_dict, field_dict):
        temp_dict = {}
                    
        for field, subfield in field_dict.items() :
            if not subfield or subfield == '' :
                sub_resultdict = result_dict[field]
            else :
                if isinstance(subfield, dict):
                    try : 
                        sub_resultdict = result_dict[field]
                        sub_resultdict = self._getresult_fielddict(sub_resultdict, subfield)
                    except :
                        pass
                    
            temp_dict[field] = sub_resultdict
            
        return temp_dict


    def find(self, collect_name, get_field=[], limits=0, condition_dict={}, iscount=False, sort_dict={}):
        
        '''
        通过mongodb的find命令获取指定字段或者所有数据
        :参数：
            collect_name：集合名
            get_field_list：获取需要的字段
            condition_dict：查询条件
            iscount：统计数量
            sort_dict：排序方式
        :返回
            一个列表
        '''

        if not self.connecter:
            self.logger.error(self.error_reason)
            return (False, self.error_reason)
        
        try :
            limits = int(limits)
        except :
            limits = 0
            
        if not sort_dict :
            sort_dict = {}
        
        collection = self.dbs[collect_name]
        if not iscount :
            try :
                if isinstance(condition_dict, dict) and condition_dict != {} :
                    condition_dict = self._handler_condition(condition_dict)
                    
                    if limits > 0 :
                        query_list = collection.find(condition_dict).limit(limits)
                    else :
                        query_list = collection.find(condition_dict)
                        
                    if sort_dict :
                        sort_list = []
                        for key , scend in sort_dict.items() :
                            if scend not in [1, -1] :
                                scend = 1
                                
                            if scend == 1 :
                                sort_list.append((key, pymongo.ASCENDING))
                            else :
                                sort_list.append((key, pymongo.DESCENDING))
                                
                        if limits > 0 :
                            try :
                                query_list = collection.find(condition_dict).sort(sort_list).limit(limits)
                            except Exception as e:
                                self.logger.error(self.log_prefix + ' 从集合' + collect_name + '查询数据失败，原因：排序查询错误，' + str(e))
                                return (False, '查询数据失败，排序查询错误，' + str(e))
                        else :
                            try :
                                query_list = collection.find(condition_dict).sort(sort_list)
                            except Exception as e:
                                self.logger.error(self.log_prefix + ' 从集合' + collect_name + '查询数据失败，原因：排序查询错误，' + str(e))
                                return (False, '查询数据失败，排序查询错误，' + str(e))
                    else :
                        if limits > 0 :
                            query_list = collection.find(condition_dict).limit(limits)
                        else :
                            query_list = collection.find(condition_dict)
                else :
                    query_list = collection.find()
                    
                result_list = self._handler_result(query_list, get_field=get_field)
                self.logger.info(self.log_prefix + ' 从集合' + collect_name + '查询数据成功')
                return (True, result_list)
            except Exception as e :
                self.logger.error(self.log_prefix + ' 从集合' + collect_name + '查询数据失败，原因：' + str(e))
                return (False, ['查询数据失败，' + str(e)])
        else :
            try :
                if isinstance(condition_dict, dict) and condition_dict != {} :
                    get_dict = self._handler_condition(condition_dict)
                    result = collection.find(get_dict).count()
                else :
                    result = collection.find().count()
                
                self.logger.info(self.log_prefix + ' 从集合' + collect_name + '查询数据后统计条数成功')
                return (True, result)
            except Exception as e :
                self.logger.error(self.log_prefix + ' 从集合' + collect_name + '查询数据后统计条数失败，原因：' + str(e))
                return (False, '查询数据失败，' + str(e))


    def find_one(self, collect_name, get_field=[], condition_dict={}):
        
        '''
        指定表的部分数据        
        :参数
            collect_name：集合名
            get_field_list：获取需要的字段
            condition_dict：查询条件
        :返回
            一个列表
        
        '''

        if not self.connecter:
            self.logger.error(self.error_reason)
            return (False, self.error_reason)
        
        condition_dict = dot2_(condition_dict)
        
        collection = self.dbs[collect_name]
        try :
            if isinstance(condition_dict, dict) :
                if condition_dict != {} :
                    condition_dict = self._handler_condition(condition_dict)
                    query_list = collection.find_one(condition_dict)
                else :
                    query_list = collection.find_one()
            else :
                query_list = collection.find_one()

            result = self._handler_result([query_list], get_field=get_field)
            self.logger.info(self.log_prefix + ' 从集合' + collect_name + '查询并返回其中一条数据成功')
            return (True, result)
        except Exception as e :
            self.logger.error(self.log_prefix + ' 从集合' + collect_name + '查询并返回其中一条数据失败，原因：' + str(e))
            return (False, '查询并返回其中一条数据失败，原因：' + str(e))
       
        
    def update(self, condition_dict, update_dict, addtime=True):
        
        '''
        通过mongodb的update命令修改数据数据，如果没有该数据，直接插入
        :参数
            collect_name：集合名
            condition_dict：查询条件
            update_dict：{'collect':集合名,'data':更新字典}
        :返回
            一个列表
        '''
        
        if not self.connecter:
            self.logger.error(self.error_reason)
            return (False, self.error_reason)
        
        try :
            collect_name = update_dict['collect']
            # 获取集合
        except Exception as e :
            self.logger.error(self.log_prefix + ' 更新数据失败，原因：参数update_dict格式出错，缺少collect，即缺少集合名')
            return (False, '更新数据失败，参数update_dict格式出错，缺少collect，即缺少集合名') 
        
        updatedict = update_dict['data']
        condition_dict = dot2_(condition_dict)
        updatedict = dot2_(updatedict)
        
        if not collect_name or not (isinstance(updatedict, dict) and updatedict != {}):
            self.logger.error(self.log_prefix + ' 从集合' + collect_name + '更新数据失败，原因：参数update_dict格式出错')
            return (False, False)
        
        collection = self.dbs[collect_name]
        condition_dict = self._handler_condition(condition_dict)
        result = collection.update(condition_dict, updatedict)
        # result 类似与{'n': 1, 'nModified': 1, 'ok': 1.0, 'updatedExisting': True}
        # {'n': 0, 'nModified': 0, 'ok': 1.0, 'updatedExisting': False}
        try :
            res_code = result['n']
            if res_code :
                self.logger.info(self.log_prefix + ' 从集合' + collect_name + '更新数据成功')
                return (True, True)
            else :
                self.logger.warn(self.log_prefix + ' 从集合' + collect_name + '更新数据失败，原因：根据查询条件无法查询到指定数据，使用插入函数进行处理')
                return self.insert(update_dict, addtime=addtime)
        except Exception as e:
            self.logger.warn(self.log_prefix + ' 从集合' + collect_name + '更新数据失败，原因：根据查询条件无法查询到指定数据，使用插入函数进行处理，' + str(e))
            return self.insert(update_dict, addtime=addtime)
  

    def group_by(self, collect, field):
        
        '''
        通过mongodb的aggregate命令进行group by计算s
        :参数
            collect_name：集合名
            filed：group by字段（或者列表、字典）
        :返回
            一个列表
        '''
        
        if not self.connecter:
            self.logger.error(self.error_reason)
            return (False, self.error_reason)

        if not isinstance(collect, str):
            self.logger.error(self.log_prefix + ' 使用group方式查询数据失败，原因：参数collect（即集合名）不为字符串')
            return (False, False)
        
        collection = self.dbs[collect]
        if isinstance(field, str) :
            condition = [{"$group":{"_id" :"$" + field}}]
        elif isinstance(field, (list, tuple)) :
            if len(field) == 1 :
                field = field[0]
                condition = [{"$group":{"_id" :"$" + field}}]
            elif len(field) == 0 :
                self.logger.error(self.log_prefix + ' 从集合' + collect + '使用group方式查询数据失败，原因：参数field（即查询字段）为空')
                return (False, False)
            else :
                temp_dict = {}
                for f in field :
                    temp_dict[f] = '$'+f

                condition = [{"$group":{"_id" :temp_dict}}]
        elif isinstance(field, dict):
            condition = [{"$group":{"_id" :field}}]
        else :
            self.logger.error(self.log_prefix + ' 从集合' + collect + '使用group方式查询数据失败，原因：参数field（即查询字段）必须是字符串、字典、列表等数据类型')
            return (False, False)
        
        try :
            query_list = collection.aggregate(condition)
        except Exception as e :
            self.logger.error(self.log_prefix + ' 从集合' + collect + '使用group方式查询数据失败，原因：' + str(e))
            return (False, False)
            
        result_list = []
        for query in query_list :
            result = query['_id']
            result_list.append(result)
           
        self.logger.info(self.log_prefix + ' 从集合' + collect + '使用group方式查询数据成功') 
        return (True, result_list)
            
    
    def remove(self, collect_name, condition_dict):
        
        '''
        删除指定数据
        :参数
            collect_name：集合名
            condition_dict：查询条件
        :返回
            一个列表
        '''
        
        if not self.connecter:
            self.logger.error(self.error_reason)
            return (False, self.error_reason)
        
        if not isinstance(condition_dict, dict):
            self.logger.error(self.log_prefix + ' 从集合' + collect_name + '删除指定数据失败，原因：条件数据类型不为字典')
            return (False, '删除指定数据失败，条件数据类型不为字典')
        
        if not condition_dict :
            self.logger.error(self.log_prefix + ' 从集合' + collect_name + '删除指定数据失败，原因：条件不能为空')
            return (False, '删除指定数据失败，条件不能为空')
        
        collection = self.dbs[collect_name]
        
        try :
            result = collection.remove(condition_dict)
            if result["ok"] == 1.0 :
                self.logger.info(self.log_prefix + ' 从集合' + collect_name + '删除指定数据成功，删除条数为' + str(result["n"]))
                return (True, '删除指定数据成功，删除条数为' + str(result["n"]))
            else :
                self.logger.error(self.log_prefix + ' 从集合' + collect_name + '删除指定数据失败，原因：' + str(result))
                return (False, result)
        except Exception as e:
            self.logger.error(self.log_prefix + ' 从集合' + collect_name + '删除指定数据失败，原因：未知错误,' + str(e))
            return (False, '未知错误，原因：' + str(e))


    def remove_all(self, collect_name):
        
        '''
        删除所有数据，尽量勿用（最好使用重命名）
        :参数
            collect_name：集合名
        :返回
            一个列表
        '''
        
        if not self.connecter:
            self.logger.error(self.error_reason)
            return (False, self.error_reason)

        collection = self.dbs[collect_name]
        
        try :
            result = collection.remove({})
            if result["ok"] == 1.0 :
                self.logger.info(self.log_prefix + ' 从集合' + collect_name + '删除所有数据成功，删除条数为' + str(result["n"]))
                return (True, '删除所有数据成功，删除条数为' + str(result["n"]))
            else :
                self.logger.error(self.log_prefix + ' 从集合' + collect_name + '删除所有数据成功，原因：' + str(result))
                return (False, '删除所有数据成功，原因：' + str(result))
        except Exception as e:
            self.logger.error(self.log_prefix + ' 从集合' + collect_name + '删除所有数据成功，原因：未知错误,' + str(e))
            return (False, '删除所有数据成功，未知错误，原因：' + str(e))


    def rename_collect(self, old_collect , new_collect):
        
        '''
        重命名集合
        :参数
            old_collect：旧集合名
            new_collect：新集合名
        :返回
            一个列表
        '''
        
        if not self.connecter:
            self.logger.error(self.error_reason)
            return (False, self.error_reason)

        collection = self.dbs[old_collect]
        
        try :
            collection.rename(new_collect)
            self.logger.info(self.log_prefix + ' 集合' + old_collect + '重命名为' + new_collect + '成功')
            return (True, '重命名成功')
        except Exception as e:
            self.logger.error(self.log_prefix + ' 集合' + old_collect + '重命名为' + new_collect + '失败，原因：' + str(e))
            return (False, '重命名失败，原因：' + str(e))

        
    def drop_collect(self, collect):
        
        '''
        删除集合
        :参数
            collect：集合名
        :返回
            一个列表
        '''
        
        if not self.connecter:
            self.logger.error(self.error_reason)
            return (False, self.error_reason)

        collection = self.dbs[collect]
        
        try :
            collection.drop()
            self.logger.info(self.log_prefix + ' 删除集合' + collect + '成功')
            return (True, '删除集合成功')
        except Exception as e:
            self.logger.info(self.log_prefix + ' 删除集合' + collect + '合败，原因：' + str(e))
            return (False, '删除失集合败，原因：' + str(e))
 
