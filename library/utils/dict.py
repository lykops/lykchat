fmt = '________'

def dot2_(data):
    
    '''
    用于处理字典的key中带有.转化为特定字符，如果写入mongodb，报错
    :parm:
        data:需要处理的字典
    '''
    
    new_data = {}
    if isinstance(data, dict) :
        for key, vaule in data.items() :
            key = key.replace('.' , fmt)
            if isinstance(vaule, dict) :
                new_data[key] = dot2_(vaule)
            else :
                new_data[key] = vaule
    return new_data


def _2dot(data):   
     
    '''
    用于处理字典的key中带有特定字符转化为.，如果写入mongodb，报错
    :parm:
        data:需要处理的字典
    '''
    
    new_data = {}
    if isinstance(data, dict) :
        for key, vaule in data.items() :
            key = key.replace(fmt , '.')
            if isinstance(vaule, dict) :
                new_data[key] = _2dot(vaule)
            else :
                new_data[key] = vaule
    return new_data


def key2dict(data) :
    if not isinstance(data, dict) or data == {} or not data:
        return (False, '参数data不是一个字典')
        
    keys_dict = {}
    for key, value in data.items() :
        v_keys_list = key2dict(value)
        if not v_keys_list[0] :
            v_keys_list = ''
        else :
            v_keys_list = v_keys_list[1]
        
        keys_dict[key] = v_keys_list
        
    keys_dict = dot2_(keys_dict)
        
    return (True , keys_dict)
            

def key2value(data, key):
    
    '''
    字典根据key获取value
    :parm
        data：字典
        key：指定key，可以是key或者key列表，如果key列表表示嵌套查询
    :return
        指定的值，如果没有为False
    例如：
        参数：
            data = {1:{2:{3:4}}}
            key = [1,2,3]
        返回：
            4
    '''
    
    if isinstance(key, str):
        try :
            return data[key]
        except :
            return ''
    elif isinstance(key, (list, tuple)) :
        if len(key) != 1:
            try :
                return key2value(data[key[0]], key[1:])
            except :
                return ''
        else :
            try :
                return data[key[0]]
            except :
                return ''


def value_replace(data, replace_dict={}):
        
    '''
        针对一个字典，把value为字符串进行替换
        :parm
            data：需要处理的字典
            replace_dict：替换规则,字典，需要替换的字符串:将要替换的字符串
    '''
        
    new_dict = {}
        
    if not isinstance(data, dict) or (not replace_dict or not isinstance(replace_dict, dict)) :
        return data
        
    for key, value in data.items() :
        if isinstance(value, str) :
            for old , new in replace_dict.items() :
                if not isinstance(old, str) or not isinstance(new, str) :
                    pass
                            
                try :
                    value = value.replace(old, new)
                except :
                    pass
                    
            new_dict[key] = value
        elif isinstance(value, dict):
            new_dict[key] = value_replace(value, replace_dict=replace_dict)
        else :
            new_dict[key] = value

    return new_dict


def get_allkey(data, prefix=''):
        
    '''
        获取字典所有key
        :parm
            data：需要处理的字典
            prefix：在key前添加的前缀
    '''
        
    key_list = []
        
    if not isinstance(data, dict) :
        return []
        
    for key, value in data.items() :
        if not prefix :
            new_prefix = str(key)
        else : 
            new_prefix = prefix + ':' + str(key)
        
        if not isinstance(value, dict) or not value :
            key_list.append(new_prefix)
        elif isinstance(value, dict):
            new_prefix = get_allkey(value, prefix=new_prefix)
            key_list.append(new_prefix)
            
    return key_list
