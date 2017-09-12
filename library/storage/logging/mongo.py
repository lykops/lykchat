from library.storage.database.mongo import Op_Mongo

class Logging_Mongo():
    def __init__(self, mongoclient=None) :
        
        '''
        该class用于写日志到mongodb服务器中
        '''
        
        if mongoclient is None :
            self.mongoclient = Op_Mongo(dest='log', idletime=1000 * 60 * 60)
            self.logger.warn('无法继承，需要初始化mongodb连接')
        else :
            self.mongoclient = mongoclient


    def write(self, oper, modeulename, content, level='debug'):
                
        '''
        写入mongo数据库
        :参数
            oper : 操作者
            content : 日志内容
            level:日志级别
            modeulename:模块名
        :返回
            一个元组，(False,原因)或者(True, 结果)
        '''
        
        if not oper :
            oper = 'unknown'
        collect = oper + '.logging'
    
        if not content :
            return (False , '日志内容为空!!!!')

        msg_dict = {
            'level':level,
            'modeule':modeulename,
            'content':content
            }

        insert_dict = {
            'collect':collect,
            'data':msg_dict
            }
        
        result = self.mongoclient.insert(insert_dict, addtime=True)
        return result


    def read(self, oper, limit=0, modeulename=None):
                
        '''
        读取mongo数据库的日志
        :参数
            oper : 操作者
            limit : 限制条数
            modeulename:模块名
        '''
        
        if not oper :
            oper = 'unknown'
        
        collect = oper + '.logging'
        
        try :
            limit = int(limit)
        except :
            limit = 0
            
        condition_dict = {}
        
        if modeulename and modeulename is not None :
            condition_dict = {'module' : modeulename}
            result = self.mongoclient.find(collect, condition_dict=condition_dict, limits=limit, sort_dict={'add_time':1})
        else :
            result = self.mongoclient.find(collect, limits=limit, sort_dict={'add_time':1})
    
        return result
        
