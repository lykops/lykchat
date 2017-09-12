import codecs
import json, re
from random import Random


def bytes2string(data, encoding='utf-8'):
    
    '''
    简单粗暴地把bytes字符串转换为str字符串
    data必须是简单bytes格式
    如果复杂，转化可能成功，但后续处理出差几率很大，请使用obj2string方法
    :parm
        data：字符串
        encoding：编码
    '''
        
    if isinstance(data, str):
        return data
    
    try :
        data = data.decode(encoding)
        # result.decode('ascii') bytes解码会得到str
    except :
        new_data = obj2string(data, encoding=encoding)
        if new_data[0] :
            data = new_data[1]
        
    return data
 

def obj2string(data, encoding='utf-8', errors=None):
    
    '''
    复杂手段，把data对象转换为str类型
    '''
    
    if isinstance(data, str):
        return (True, data)
    
    try:
        codecs.lookup_error('surrogateescape')
        has_surr = True
    except LookupError:
        has_surr = False
    
    error_list = frozenset((None, 'surrogate_or_escape', 'surrogate_or_strict', 'surrogate_then_replace'))
    if errors in error_list:
        if has_surr:
            errors = 'surrogateescape'
        elif errors == 'surrogate_or_strict':
            errors = 'strict'
        else:
            errors = 'replace'

    if isinstance(data, bytes):
        return (True,data.decode(encoding, errors))

    try:
        value = str(data)
        return (True, value)
    except UnicodeError:
        try:
            value = repr(data)
            return (True, value)
        except UnicodeError:
            return (False,'未知错误')
          
    return (False, '未知错误')
 

def obj2bytes(data, encoding='utf-8', errors=None):
    
    '''
    复杂手段，把data对象转换为bytes类型
    '''
    
    if isinstance(data, bytes):
        return (True, data)
    
    try:
        codecs.lookup_error('surrogateescape')
        has_surr = True
    except LookupError:
        has_surr = False
    
    error_list = frozenset((None, 'surrogate_or_escape', 'surrogate_or_strict', 'surrogate_then_replace'))
    original_errors = errors
    if errors in error_list:
        if has_surr:
            errors = 'surrogateescape'
        elif errors == 'surrogate_or_strict':
            errors = 'strict'
        else:
            errors = 'replace'

    if isinstance(data, str):
        try:
            # 试图使用更快的方式处理
            return (True, data.encode(encoding, errors))
        except UnicodeEncodeError:
            if original_errors in (None, 'surrogate_then_replace'):
                # 虽慢，但让然可以工作
                return_string = data.encode('utf-8', 'surrogateescape')
                return_string = return_string.decode('utf-8', 'replace')
                return (True, return_string.encode(encoding, 'replace'))
            else :
                try :
                    data = data.encode(encoding)
                    return (True, data)
                except Exception as e:
                    return (False, str(e))
    
    try :
        data = str(data)
        data = data.encode(encoding)
        return (True, data)
    except Exception as e:
        return (False, str(e))
        
    return (False, '位置错误')


def string2bytes(data, encoding='utf-8'):
    
    '''
    简单粗暴把字符串转换为bytes类型
    data必须是简单字符串
    如果复杂的字符串，转化可能成功，但后续处理出差几率很大，请使用obj2bytes方法
    :parm
        data：字符串
    '''
    
    if isinstance(data, bytes):
        return data
    
    try :
        data = data.encode(encoding)
        # result.encode('ascii') str编码会变成bytes
    except :
        new_data = obj2bytes(data, encoding=encoding)
        if new_data[0] :
            data = new_data[1]
        
    return data


def dict2string(data, cnfmt='=', sprfmt='\n', recursion=False):
    '''
    字典格式转化为字符串
    :param:
        data：需要转化的字典
        sprfmt：分隔符
        cnfmt：键值的连接符
        recursion：是否递归
    :return：
        strings：转化后的字符串
    '''
    strings = ''
    if isinstance(data, dict):
        for key , vaule in data.items() :
            key = str(key)
            
            if isinstance(vaule, dict) :
                vaule = '\n' + dict2string(vaule, cnfmt=cnfmt, sprfmt=sprfmt)
            elif isinstance(vaule, (list, tuple)) :
                vaule = list2string(vaule, sprfmt=sprfmt)
            elif isinstance(vaule, (int, float, str)) :
                vaule = str(vaule)
            else :
                vaule = str(vaule)
            
            strings = strings + key + cnfmt + vaule + sprfmt
    else :
        strings = False
        # 如果不是字典的话，直接返回False
    
    return strings


def list2string(data, sprfmt='\n', recursion=False):
    '''
    列表、元组格式转化为字符串
    :param:
        data：需要转化的字典
        sprfmt：分隔符
        recursion：是否递归
    :return：
        strings：转化后的字符串
    '''
    strings = ''
    if isinstance(data, (list, tuple)):
        for vaule in data :
            if isinstance(vaule, dict) :
                vaule = dict2string(vaule, cnfmt='=', sprfmt=sprfmt)
            elif isinstance(vaule, (list, tuple)) :
                vaule = list2string(vaule, sprfmt=sprfmt)
            elif isinstance(vaule, (int, float, str)) :
                vaule = str(vaule)
            else :
                vaule = str(vaule)
            
            strings = strings + vaule + sprfmt
    else :
        strings = False
        # 如果不是字典的话，直接返回False
    
    return strings


def random_str(ranlen=8):
    strings = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(ranlen):
        i = i
        strings = strings + chars[random.randint(0, length)]
    return strings


def str2json(string):
    
    '''
    字符串转化为json格式
    json的标准格式：要求必须只能使用双引号作为键或者值的边界符号，不能使用单引号，而且“键”必须使用边界符（双引号）
    :parm
        string：需要转化的字符串
    '''
    
    if not isinstance(string, str) :
        return (True, string)
    
    if not re.search('"' , string) and re.search("'", string) :
        delimiter = '!!!!!!!!!!!!!'
        b = string.replace('"', delimiter)
        c = b.replace("'", '"')
        string = c.replace(delimiter, "'")
    elif not re.search('"' , string) and not re.search("'", string) :
        a = string.replace(', ', '", "')
        b = a.replace("[", '["')
        string = b.replace("]", '"]')
        
    try :
        result = json.dumps(string)
        return (True, result)
    except Exception as e:
        return (False, str(e))


def str2dict(string):
    
    '''
    字符串转化为字典
    json的标准格式：要求必须只能使用双引号作为键或者值的边界符号，不能使用单引号，而且“键”必须使用边界符（双引号）
    :parm
        string：需要转化的字符串
    '''
    
    if not isinstance(string, str) :
        return (True, string)
    
    if not re.search('"' , string) and re.search("'", string) :
        delimiter = '!!!!!!!!!!!!!'
        b = string.replace('"', delimiter)
        c = b.replace("'", '"')
        string = c.replace(delimiter, "'")
        
    try :
        result = json.loads(string)
        return (True, result)
    except Exception as e:
        return (False, str(e))
    
    
def str2list(string):
    
    '''
    字符串转化为列表
    json的标准格式：要求必须只能使用双引号作为键或者值的边界符号，不能使用单引号，而且“键”必须使用边界符（双引号）
    :parm
        string：需要转化的字符串
    '''
    
    if not isinstance(string, (list, tuple)) :
        string = list(string)
        return (True, string)
    
    if not isinstance(string, str) :
        string = str(string)
        # return (True, string)
    
    if not re.search('"' , string) and re.search("'", string) :
        delimiter = '!!!!!!!!!!!!!'
        b = string.replace('"', delimiter)
        c = b.replace("'", '"')
        string = c.replace(delimiter, "'")
    elif not re.search('"' , string) and not re.search("'", string) :
        a = string.replace(', ', '", "')
        b = a.replace("[", '["')
        string = b.replace("]", '"]')
        
    try :
        result = json.loads(string)
        return (True, result)
    except Exception as e:
        return (False, str(e))


