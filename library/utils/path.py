import os, time

def make_dir(directory, chmods=755 , force=True , backup=True) :
    '''
    用于创建目录
    :parm
        directory:创建目录
        chmods：权限，必须是数字，例如755
        force：当目录存在，强制执行
        backup：当目录存在，备份文件，后缀名为%Y%m%d%H%M%S-bk
    :return
        True：成功
        Flase：失败
    '''
    if os.path.exists(directory) :
        if not force :
            return False
        
        dt = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        if backup :
            try : 
                pre_result = os.renames(directory , directory + '-' + str(dt) + '-' + 'bk')
            except Exception as e :
                pre_result = str(e)
        else : 
            pre_result = False
            '''
            #result = os.removedirs(dir)
            try : 
                result = os.renames(directory , directory + '-' + str(dt) + '-' + 'bk')
            except Exception as e :
                result = str(e)
            '''
    else :
        pre_result = False
    
    if not pre_result :
        try :
            chmods = int(chmods)
        except :
            chmods = 755
        
        try :
            result = os.makedirs(directory, chmods, exist_ok=True)
        except Exception as e :
            result = str(e)
    else :
        result = False
        
    if not result :
        result = True
    else :
        result = False
        
    return result
 
 
def get_pathlist(this_dir, get_death=1, curr_death=1, isonlyfile=True , isonlyaccess=True, max_size=0):
    
    '''
    获取指定目录下指定深度的所有目录和文件
    :parm
        this_dir：指定目录
        get_death：指定深度，该值不会出现变化，0表示递归最大层次（10层），1表示当前目录下文件和目录，不递归
        curr_death：当前深度，仅用于递归调用
        isonlyfile：是否只返回文件，不返回目录等
        max_size：最大文件大小，只显示文件大小小于该值的文件，单位bytes，0者不显示
    '''

    try :
        get_death = int(get_death)
    except :
        get_death = 1
        
    if get_death >= 10 or get_death == 0 :
        get_death = 10
        
    try :
        curr_death = int(curr_death)
    except :
        curr_death = 1
    
    if isinstance(this_dir, str) :
        if not this_dir :
            return (False, "给定参数this_dir不能为空")
    else :
        return (False, "给定参数this_dir不是一个字符串")

    dir_list = []
    
    try :
        dlist = os.listdir(this_dir)
    except :
        return (True, [this_dir])
    
    for subdir in dlist:
        full_subdir = this_dir + '/' + subdir

        try :
            full_subdir = os.path.realpath(os.path.expanduser(full_subdir))
        except :
            if not isonlyaccess :
                dir_list.append(full_subdir)
            continue

        if os.path.isfile(full_subdir):
            try :
                max_size = int(max_size)
            except :
                max_size = 0
                
            if max_size >= 0 :
                filesize = os.path.getsize(full_subdir)
                if filesize >= max_size :
                    continue
            
            dir_list.append(full_subdir)
        elif os.path.isdir(full_subdir) and get_death > curr_death:
            subdir_list = get_pathlist(full_subdir, get_death=get_death, curr_death=curr_death + 1, isonlyfile=isonlyfile, isonlyaccess=isonlyaccess, max_size=max_size)
            if subdir_list[0] :
                dir_list = dir_list + subdir_list[1]
        else : 
            if not isonlyaccess :
                dir_list.append(full_subdir)
            continue
                
    return (True, dir_list)


def get_basedir(this_path):
    from library.utils.file import check_fileaccessible
    this_path = check_fileaccessible(this_path)
    if not this_path[0] :
        return this_path
    
    this_path = this_path[1]
    this_basedir = os.path.dirname(this_path)
    return (True , this_basedir)
