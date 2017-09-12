import time , re


def datetime2timestamp(timestr):
    '''
    时间转化为时间戳
    :parm
        timestr ：时间，支持的格式有：
            Y/m/d【 H:M:S】
            Y-m-d【 H:M:S】
            Y年m月d日【 H:M:S】
    :return
        时间戳或者False
    '''
    try :
        (convert_after, old_format) = datetime2format(timestr)
        if convert_after == False or old_format == False :
            return False
    except :
        return False
    
    try :
        strptimes = time.strptime(convert_after, old_format)
    except :
        return False
    
    return time.mktime(strptimes)


def timestamp2datetime(stamp=0 , fmt='%Y-%m-%d %H:%M:%S'):
    '''
    将时间戳转化指定格式的时间
    :parm :
        stamp：时间戳，如果没有指定表示当前时间，如果不是数字型，返回错误
        smt：转化时间格式
    :return :
        转化后的时间
    '''

    try :
        stamp = float(stamp)
    except :
        return False

    if int(stamp) == 0 :
        stamp = time.time()

    try :
        strptm = time.localtime(stamp)
    except :
        return False

    return time.strftime(fmt , strptm)


def datetime2format(timestr):
    '''
    用于时间转化为时间格式，并会检查日期是否有效
        如果日期在1000-4999年内视为有效
        小时、分钟、秒钟不符合逻辑，将剔除掉后面部分
    :parm
        timestr ：时间，支持的格式有：
            Y/m/d【 H:M:S】
            Y-m-d【 H:M:S】
            Y年m月d日【 H:M:S】
    :return
        一个元组，包括新的时间和时间格式，(new_datetime, datetime_fmt)
    '''
    datetime_list = timestr.split(' ')
    datestr = datetime_list[0]
    
    datestr = datestr.replace('/' , '-')
    datestr = datestr.replace('年' , '-')
    datestr = datestr.replace('月' , '-')
    datestr = datestr.replace('日' , '')

    date_list = datestr.split('-')
    if len(date_list) == 3 :
        year = date_list[0]
        if re.search('^[0-9]{2}$', year) :
            yearfmt = '%y-'
        elif re.search('^[1-4][0-9]{3}$', year) or re.search('^[1-9][0-9]{2,3}$', year) :
            yearfmt = '%Y-'
        else :
            return (False, False)
        
        mouth = date_list[1]
        if re.search('^[0-1][0-9]$', mouth) or re.search('^[1-9]$', mouth):
            if int(mouth) > 0 and int(mouth) < 13 :
                pass
            else :
                return (False, False)
            
            mouthfmt = '%m-'
        else :
            return (False, False)
        
        day = date_list[2]
        if re.search('^[0-3][0-9]$', day) or re.search('^[1-9]$', day):
            if int(day) > 0 and int(day) < 32 :
                pass
            else :
                return (False, False)
            
            dayfmt = '%d'
        else :
            return (False, False)
        datefmt = yearfmt + mouthfmt + dayfmt
    else :
        return (False, False)
    
    new_datetime = datestr
    
    try :
        timestr = datetime_list[1]
    except :
        timestr = False
        
    timefmt = ''
    if timestr :
        time_list = timestr.split(':')
        for i in range(len(time_list)) :
            if i == 0 :
                hour = time_list[i]
                if re.search('^[0-2][0-9]$', hour) or re.search('^[0-9]$', hour):
                    if int(hour) >= 0 and int(hour) < 24 :
                        pass
                    else :
                        timefmt = ''
                        break
                    
                    new_datetime = new_datetime + ' ' + hour
                    hourfmt = '%H'
                else :
                    timefmt = ''
                    break
        
            if i == 1 :
                minu = time_list[i]
                if re.search('^[0-5][0-9]$', minu) or re.search('^[0-9]$', minu):
                    minfmt = ':%M'
                    new_datetime = new_datetime + ':' + minu 
                else :
                    timefmt = ' ' + hourfmt
                    break
                
            if i == 2 :
                sec = time_list[i]
                if re.search('^[0-5][0-9]$', sec) or re.search('^[0-9]$', sec):
                    secfmt = ':%S'
                    timefmt = ' ' + hourfmt + minfmt + secfmt
                    new_datetime = new_datetime + ':' + sec
                else :
                    timefmt = ' ' + hourfmt + minfmt
                    break
                
    datetime_fmt = datefmt + timefmt
    return (new_datetime, datetime_fmt)
    

def datetime2datetime(timestr , fmt):
    '''
    根据指定的时间格式转换时间
    :parm
        timestr ：时间或者时间戳，支持的格式有：
            Y/m/d【 H:M:S】
            Y-m-d【 H:M:S】
            Y年m月d日【 H:M:S】
    :return
        时间或者False
    '''
    if isinstance(timestr, (float,int)) :
        stamp = timestr
    elif isinstance(timestr, str) :
        try :
            stamp = float(timestr)
        except :
            stamp = datetime2timestamp(timestr)
            if stamp == False :
                return False
    else : 
        return False
    
    try :
        newvalue = timestamp2datetime(stamp=stamp, fmt=fmt)
        return newvalue
    except :
        return False
