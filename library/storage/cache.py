from library.storage.database.redis_api import Op_Redis

class Manager_Cache():
    def __init__(self, redisclient=None):
        if redisclient is None :
            self.redisclient = Op_Redis()
        else :
            self.redisclient = redisclient
    
    
    def write(self, redis_key, data, expire=60 * 60, ftm='obj'):
        try :
            self.redisclient.delete(redis_key)
        except :
            pass
        
        set_dict = {
            'name' : redis_key,
            'value' : data,
            'ex':expire
            }
                
        result = self.redisclient.set(set_dict, fmt=ftm)
        return result


    def read(self, redis_key, ftm='obj'):
        result = self.redisclient.get(redis_key, fmt=ftm)
        return result


    def delete(self, redis_key):
        result = self.redisclient.delete(redis_key)
        return result
