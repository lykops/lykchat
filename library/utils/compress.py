'''
gz： 即gzip，通常只能压缩一个文件。与tar结合起来就可以实现先打包，再压缩。
tar： linux系统下的打包工具，只打包，不压缩
tgz：即tar.gz。先用tar打包，然后再用gz压缩得到的文件
zip： 不同于gzip，虽然使用相似的算法，可以打包压缩多个文件，不过分别压缩文件，压缩率低于tar。
rar：打包压缩文件，最初用于DOS，基于window操作系统。压缩率比zip高，但速度慢，随机访问的速度也慢。
'''

import os
import tarfile , zipfile, rarfile, gzip

from library.utils.file import get_filetype
from library.utils.path import make_dir


def uncompress(src_file, dest_dir):
    result = get_filetype(src_file)
    if not result[0] :
        return (False, result[1], '')
    filefmt = result[1]
            
    if filefmt not in ('zip') :
        return (False, '本系统暂时只支持解压zip格式的文件')
    
    result = make_dir(dest_dir)
    if not result :
        return (False, '创建解压目录失败', filefmt)

    if filefmt in ('tgz', 'tar') :
        try :
            tar = tarfile.open(src_file)  
            names = tar.getnames()   
            for name in names:  
                tar.extract(name, dest_dir)  
            tar.close()
        except Exception as e :
            return (False, e, filefmt)
    elif filefmt == 'zip':
        try :
            zip_file = zipfile.ZipFile(src_file)  
            for names in zip_file.namelist():  
                zip_file.extract(names, dest_dir)  
            zip_file.close()  
        except Exception as e :
            return (False, e, filefmt)
    elif filefmt == 'rar' :
        try :
            rar = rarfile.RarFile(src_file)  
            os.chdir(dest_dir)
            rar.extractall()  
            rar.close()  
        except Exception as e :
            if str(e) == "Unrar not installed? (rarfile.UNRAR_TOOL='unrar')" :
                return (False, '请在服务器上安装unrar，yum install -y unrar', filefmt) 
            
            return (False, e, filefmt)
    elif filefmt == 'gz' :
        try :
            f_name = dest_dir + '/' + os.path.basename(src_file)
            # 获取文件的名称，去掉  
            g_file = gzip.GzipFile(src_file)  
            # 创建gzip对象  
            open(f_name, "w+").write(g_file.read())  
            # gzip对象用read()打开后，写入open()建立的文件中。  
            g_file.close()  
            # 关闭gzip对象  
            
            result = get_filetype(src_file)
            if not result[0] :
                new_filefmt = '未知'
            else :
                new_filefmt = result[1]
            return (True, '解压后的文件格式为：' + new_filefmt, filefmt)

            
            '''
            suffix = os.path.splitext(src_file)[-1]
            if suffix :
                f_name = src_file.replace(suffix, "") 
            else :
                f_name = src_file + '_' + random_str()
            #获取文件的名称，去掉  
            g_file = gzip.GzipFile(src_file)  
            #创建gzip对象  
            open(f_name, "w+").write(g_file.read())  
            #gzip对象用read()打开后，写入open()建立的文件中。  
            g_file.close()  
            #关闭gzip对象  
            
            result = get_filetype(src_file)
            if not result[0] :
                return (False, result[1], '')
            new_filefmt = result[1]
            return (True, '解压后的文件格式为：' + new_filefmt, filefmt)
            result = uncompress(f_name, dest_dir)
            if not result[0] :
                new_filefmt = result[2]
                if new_filefmt not in ('gz','tar','tgz','zip' ,'rar') :
                    return (True, '解压后的文件格式为：' + new_filefmt, filefmt)
                else :
                    return (False, '解压后的文件格式不支持或者不是压缩文件', filefmt)
            '''
            
        except Exception as e :
            return (False, e, filefmt)
    else :
        return (False, '文件格式不支持或者不是压缩文件', filefmt)
        
    return (True, '', filefmt)
