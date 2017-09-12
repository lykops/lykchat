import yaml

from library.utils.file import read_file

def yaml_loader(data, data_type='data'):
    
    '''
    解析yaml，把yaml文件或者字符串解析成为yaml列表格式
    :参数
        data：yaml文件或任意类型数据
        data_type：数据类型，目前只能接受file或者data，默认为data
    :返回
        元组：(bool, 列表或者错误信息)
    '''
    
    if data_type not in ('file' , 'data') :
        return (False, 'data_type参数不正确，只能为file或者data')
    
    if data_type == 'file' :
        result = read_file(data)
        if result[0] :
            data = result[1]
        else :
            return result

    try :
        yaml_data = yaml.load(data)
        return (True, yaml_data)
    except Exception as e:
        try :
            reuslt = yaml.dump(data)
            if reuslt :
                return (True, data)
            else :
                return (False, '不能被yaml加载，原因：' + str(e))
        except Exception as e:
            return (False, '不能被yaml加载，原因：' + str(e))


def yaml_dumper(data, file=None):
    
    '''
    把yaml列表写入yaml文件
    :参数
        data:yaml列表
        file:需要写入yaml文件名
    :返回
        元组：(bool, 文件名或者错误信息)
    '''
    
    try :
        yaml_data = yaml.dump(data)
        return (True, yaml_data)
    except Exception as e:
        return (False, e)
    
