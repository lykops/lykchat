import re

def contain_zh(word):
    '''
    判断传入字符串是否包含中文
    :param 
        word: 待判断字符串
    :return: 
        True:包含中文  
        False:不包含中文
    '''
    zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')

    if not isinstance(word, (str, list, tuple)) :
        return False
    
    try :
        word = word.decode()
    except :
        pass
    match = zh_pattern.search(word)
    return match


def contain_spec_symbol(word):

    '''
    判断传入字符串是否包含特殊字符，'!"#$%&\'()*+,:;<=>?@[\\]^`{|}~ '
    :param 
        word: 待判断字符串
    :return: 
        True:包含 
        False:不包含
    '''
    
    spec_symbol = '!"#$%&\'()*+,:;<=>?@[\\]^`{|}~ '

    if not isinstance(word, (str, list, tuple)) :
        return False
    
    for s in word :
        if s in spec_symbol :
            return True

    return False


def contain_only_letter_number(word):

    '''
    判断传入字符串(或者是列表)只包含字母和数字
    :param 
        word: 待判断字符串
    :return: 
        True:包含 
        False:不包含
    '''
    
    letter_number = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'

    if not isinstance(word, (str, list, tuple)) :
        return False
    
    for s in word :
        if s not in letter_number :
            return False

    return True
