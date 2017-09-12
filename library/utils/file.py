import os, time, stat, subprocess, re, filetype

from library.utils.path import make_dir
from library.utils.type_conv import bytes2string
from library.utils.type_conv import random_str
from lykchat.settings import BASE_DIR

def write_file(file , mode , content, force=False , backup=True):
    
    '''
    用于把指定内容写入文件
    :parm
        file:写入文件
        mode：打开文件模式，必须为写
        content：写入文件内容
        force：当文件存在，强制执行
        backup：当文件存在，备份文件，后缀名为%Y%m%d%H%M%S-bk
    :return
        True：成功
        Flase：失败
    '''
    
    if 'w' not in mode and 'a' not in mode and '+' not in mode :
        return (False, '参数mode只能含有写模式（必须含有w、a、+）')
    
    if not isinstance(file, str) :
        return (False, '参数file只能为字符串')
    
    if os.path.exists(file) :
        if os.path.isdir(file) :
            return (False, file + '是一个存在的目录')
        else :
            if not 'a' in mode :
                if not force :
                    return (False, file + '文件存在')
                
                if backup == True :
                    try : 
                        dt = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                        pre_result = os.renames(file , file + '-' + str(dt) + '-' + 'bk')
                    except Exception as e :
                        pre_result = str(e)
                else :
                    pre_result = False
            else :
                pre_result = False
    else :
        dirname = os.path.dirname(file)
        if os.path.exists(dirname) : 
            if not os.path.isdir(dirname) :
                return (False, '目录为文件')
        else :
            mkresult = make_dir(dirname)
            if not mkresult :
                return (False, '无法创建目录')
        
        pre_result = False
        
    content = bytes2string(content)
    content = str(content)
        
    if not pre_result :
        try :
            pf = open(file, mode)
            pf.writelines(content + '\n')
            pf.close()
            return (True, file)
        except Exception as e :
            rescode = False
            result = str(e)
    else :
        rescode = False
        result = '未知错误'
        
    return (rescode, result)
             
    
def read_file(file, mode=False , sprfmt='\n', outfmt='string'):
    '''
    用于读取文件内容或者执行文件
    :parm
        file:读取或者执行文件名，支持当前相对路径、~、或者绝对路径
        mode：是否执行，Flase为普通文件，其他为执行文件
        sprfmt：换行符
        outfmt：输出格式
            bytes：转化为bytes格式，主要是用于解决ansible
            string：转化为字符串格式
            raw：原始文档，不作任何处理
    :return
        返回一个(执行结果代码，内容)
        执行结果代码：Flase失败，True成功
        内容：成功为执行或者读取内容，失败为失败原因
    '''
    
    (code , this_path) = check_fileaccessible(file)
    if not code :
        return (code , this_path)

    if mode:
        try:
            p = subprocess.Popen(this_path, stdout=subprocess.PIPE)
        except Exception as e:
            return (False, '执行失败，' + str(e))
            
        stdout, stderr = p.communicate()
        resultcode = p.returncode
        if resultcode != 0:
            return (False, '执行过程中出现错误，返回错误代码为' + resultcode)
        
        if stderr :
            pass

        content = stdout
        sprfmt = b'\n'
        content = stdout.strip(sprfmt)
        if outfmt == 'bytes' or outfmt == 'raw' :
            pass
        else :
            content = bytes2string(content)
    else:
        try:
            if outfmt == 'bytes' :
                fp = open(this_path, "rb")
            else :
                fp = open(this_path, "r")
                    
            content = fp.read().strip()
            fp.close()
        except Exception as e:
            return (False, '读取失败，' + str(e))

    return (True, content)


def check_fileaccessible(this_path):
    
    '''
    检查文件是否可以访问
    :parm
        file:需要检查的文件，支持当前相对路径、~、或者绝对路径
    :return
        返回一个(执行结果代码，原因)
        执行结果代码：Flase失败，True成功
        原因：成功为True，失败为失败原因
    '''
    
    result = path_isexists(this_path)
    if result[0] :
        this_path = result[1]
    else :
        return result
    
    if not os.path.isfile(this_path) :
        return (False, '路径存在，但不是一个文件')
    
    if not (os.path.isfile(this_path) or stat.S_ISFIFO(os.stat(this_path).st_mode)):
        return (False, "该文件没有权限访问")
    
    return (True, this_path)


def path_isexists(this_path):
    
    '''
    检查文件路径是否存在
    :parm
        this_path:需要检查的路径，支持当前相对路径、~、或者绝对路径
    :return
        返回一个(执行结果代码，原因)
        执行结果代码：Flase失败，True成功
        原因：成功为True，失败为失败原因
    '''
    
    if not isinstance(this_path, str) :
        return (False, '参数错误，只能为字符串')
    
    this_path = os.path.realpath(os.path.expanduser(this_path))
    this_dir = os.path.dirname(this_path)
    if not os.path.exists(this_dir):
        return (False, this_path + "的上级目录不存在")
    
    try :
        if not os.path.exists(this_path):
            return (False, this_path + "不存在")
    except :
        this_path = this_path + '/'
        if not os.path.exists(this_path):
            return (False, this_path + "不存在")

    return (True, this_path)


def read_file_grep(file , kw_list, isrecursion=False, delimiter='', row_list=[]):
    
    '''
    使用cat+grep命令方式读取文件内容
    :parm
        file:文件
        kw_list:关键字列表
        isrecursion:是否分割每行
        delimiter:行的字段分隔符
        row_list:需要列的列表
    '''
    
    (code , this_path) = check_fileaccessible(file)
    if not code :
        return (code , this_path)

    from library.utils.syscmd import os_popen
    syscmd = 'cat ' + this_path 
    
    if isinstance(kw_list, (list,tuple)) and kw_list:
        for kw in kw_list :
            syscmd = syscmd + '| grep ' + kw
            
    rescd, content = os_popen(syscmd, outftm='list' , isrecursion=isrecursion, delimiter=delimiter)
    
    if not rescd :
        return  (code , this_path)
    
    if isrecursion and (isinstance(row_list, (list, tuple)) and row_list) :
        temp_list = []
        for line in content :
            temp_l = []
            for row in row_list :
                try :
                    temp_l.append(line[row - 1])
                except :
                    pass
                
            temp_list.append(temp_l)
        
        content = temp_list
    
    return (True, content)
            

def write_random_file(data):
    for i in range(10) :
        temp_file = '/dev/shm/lykops/' + random_str(ranlen=30) + str(i) + '_' + str(time.time())
        result = write_file(temp_file, 'w', data)
        if result[0] :
            return (True, temp_file)
        
    return (False, '临时文件无法写入/dev/shm/lykops/')


def upload_file(file, upload_dir='', filename='', max_upload_size=1024 * 1024, chmods='444', force=False):
    
    '''
    用于web页面上传文件
    :parm
        file：上传文件内容
        upload_file：上传目录，默认：在项目根目录下的/file/upload
        filename：上传后的文件名，默认：10个随机字符+_+文件名
        max_upload_size：最大上传文件大小，默认为1M
    :return
        False：上传失败
        filename：上传成功后的文件名
    '''
    
    try :
        if file.size > max_upload_size:
            return (False, '上传文件超过最大值')
        
        if not filename :
            filename = random_str(ranlen=10) + '_' + file.name
    except Exception as e:
        return (False, '可能是参数file出问题，' + str(e))
    
    if upload_dir :
        result = path_isexists(upload_dir)
        if not result[0] :
            upload_dir = os.path.join(BASE_DIR, 'file/upload/')
            make_dir(upload_dir, force=False , backup=False)
    else :
        upload_dir = os.path.join(BASE_DIR, 'file/upload/')
        make_dir(upload_dir, force=False , backup=False)
        
    this_path = str(upload_dir) + str(filename)
    this_path = this_path.replace(' ' , '\\ ')
    result = path_isexists(upload_dir)
    if not result[0] :
        return (False, '上传目录不存在')
    
    if force and os.path.exists(this_path) :
        try :
            os.rename(this_path, this_path + '_bk_' + random_str(ranlen=10))
        except :
            pass
    
    
    with open(this_path, 'wb+') as dest:
        for chunk in file.chunks():
            dest.write(chunk)
            
        os.system('chmod ' + str(chmods) + ' ' + this_path)
        return (True, this_path)
    
    return (False, '未知错误')
    
    
def chmod(this_path, mode='444'):
    
    
    '''
    stat.S_ISUID: Set user ID on execution 不常用
    stat.S_ISGID: Set group ID on execution 不常用
    stat.S_ENFMT: Record locking enforced 不常用
    stat.S_ISVTX: Save text image after execution 在执行之后保存文字和图片
    stat.S_IREAD: Read by owner 对于拥有者读的权限
    stat.S_IWRITE: Write by owner 对于拥有者写的权限
    stat.S_IEXEC: Execute by owner 对于拥有者执行的权限
    stat.S_IRWXU:: Read, write, and execute by owner 对于拥有者读写执行的权限
    stat.S_IRUSR: Read by owner 对于拥有者读的权限
    stat.S_IWUSR: Write by owner 对于拥有者写的权限
    stat.S_IXUSR: Execute by owner 对于拥有者执行的权限
    stat.S_IRWXG: Read, write, and execute by group 对于同组的人读写执行的权限
    stat.S_IRGRP: Read by group 对于同组读的权限
    stat.S_IWGRP: Write by group 对于同组写的权限
    stat.S_IXGRP: Execute by group 对于同组执行的权限
    stat.S_IRWXO: Read, write, and execute by others 对于其他组读写执行的权限
    stat.S_IROTH: Read by others 对于其他组读的权限
    stat.S_IWOTH: Write by others 对于其他组写的权限
    stat.S_IXOTH: Execute by others 对于其他组执行的权限
    
    '''
    
    if not mode :
        mode = '444'
        
    mode = str(mode)
    
    chmod_list = [
        {
            '4' : 'stat.S_IREAD',
            '5' : 'stat.S_IEXEC',
            '6' : 'stat.S_IWRITE',
            '7' : 'stat.S_IRWXU',
        },
        {
            '4' : 'stat.S_IRGRP',
            '5' : 'stat.S_IXGRP',
            '6' : 'stat.S_IWGRP',
            '7' : 'stat.S_IRWXG',
        },
        {
           '4' : 'stat.S_IROTH',
           '5' : 'stat.S_IXOTH',
           '6' : 'stat.S_IWOTH',
           '7' : 'stat.S_IRWXO',
        },
        ]
    
    mode_len = len(mode)
    if mode_len > 3 :
        mode = '444'
        
    if mode_len == 1:
        mode = mode + '44'
        
    if mode_len == 2:
        mode = mode + ' 4'
        
    try :
        temp_str = chmod_list[0][mode[0]]
    except :
        temp_str = chmod_list[0]['4']
               
    try :
        temp_str = temp_str + '|' + chmod_list[1][mode[1]]
    except :
        temp_str = temp_str + '|' + chmod_list[1]['4']
           
    try :
        temp_str = temp_str + '|' + chmod_list[2][mode[2]]
    except :
        temp_str = temp_str + '|' + chmod_list[2]['4']
          
    try :
        os.chmod(this_path, temp_str)
    except :
        pass


def get_filetype(this_path):
    
    '''
    获取文件类型
    '''
    
    result = check_fileaccessible(this_path)
    if not result[0] :
        return result
    
    this_path = result[1]
    
    kind = filetype.guess(this_path)
    if kind is not None:
        return (True, kind.extension, kind.mime)
    
    output = os.popen('file --mime-type ' + this_path + ' | gawk {"print $2"}')
    mime_str = output.read()
    mime_str = mime_str.replace('\n', '')
    mime_type = re.split(': ', mime_str)[0]
    # /opt/lykops/example/ansible/playbook/ntpdate.yaml: text/plain
    if re.search('text/plain$', mime_type) :
        suffix = 'txt'
    else :
        suffix = os.path.splitext(this_path)[-1]
    return (True, suffix, mime_type)
    
