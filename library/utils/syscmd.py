import os, re
def os_popen(syscmd, outftm='list', isrecursion=False, delimiter=' '):
    
    '''
    使用os.popen执行系统命令
    :parm
        syscmd:系统命令
        outftm:输出格式
        isrecursion:是否递归到行
        delimiter:分隔符
    '''
    
    output = os.popen(syscmd)
    content = output.read()
    
    if outftm == 'list':
        result = re.split('\n' , content)
        if isrecursion :
            result_list = []
            for line in result :
                res = re.split(delimiter , line)
                result_list.append(res)
            return (True, result_list)
        else :
            return (True, result)
        
        return (True, result)
    else :
        return (True, content)
