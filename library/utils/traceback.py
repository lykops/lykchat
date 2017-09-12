import traceback


def get_traceback(fmt='str'):
    '''
    追溯代码执行位置
    :参数
        fmt：指定返回数据类型
    :返回
        根据参数fmt返回指定数据类型
    '''
    caller_list = traceback.extract_stack()
    caller_list = caller_list[:-1]
    
    return_list = []
    return_str = '\t追源日志：\n'
    return_dict = {}
    
    for caller in caller_list :
        caller_sn = caller_list.index(caller) + 1
        caller_file = caller[0]
        caller_row = caller[1]
        caller_func = caller[2]
        
        if caller_func == '<module>' :
            caller_func = 'None'    
                
        caller_content = caller[3]
    
        if return_str :
            return_str = return_str + '\t\t第' + str(caller_sn) + '层\t文件名：' + caller_file + '的第' + str(caller_row) + '行，模块名：' + caller_func + '，代码内容：' + caller_content + '\n'
        else:
            return_str = '\t\t第' + str(caller_sn) + '层\t文件名：' + caller_file + '的第' + str(caller_row) + '行，模块名：' + caller_func + '，代码内容：' + caller_content + '\n'
            
        caller_tuple = (caller_sn , caller_file, caller_row, caller_func, caller_content)
        return_list.append(caller_tuple)
        
        return_dict[str(caller_sn)] = {
            'file' : caller_file,
            'row' : caller_row,
            'func' : caller_func,
            'content' :caller_content
            }
                    
    if fmt == 'list' :
        return return_list
    elif fmt == 'dict' :
        return return_dict
    else :
        return return_str
