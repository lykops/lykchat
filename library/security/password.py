import re, logging
from django.contrib.auth.hashers import make_password

class Manager_Password():
    '''
    对密码进行加密和校验等功能
    '''
    def __init__(self):
        self.logger = logging.getLogger("security")
        self.type = 'pbkdf2_sha256'  # 加密方式
        self.min_len = 8  # 最短长度
        self.fixed_field = 'lykops'  # 固定的字段


    def encryt(self, cleartext, is_validate=True):
        
        '''
        密码加密
        :parm
            cleartext：明文密码
            is_validate：是否需要验证密码长度
        '''
        
        if is_validate :
            result = self._validate(cleartext)
            if not result[0] :
                self.logger.error('密码加密失败，原因：提供的密码无法通过密码复杂度检查，' + str(result[1]))
                return (False, '提供的密码无法通过密码复杂度检查，' + str(result[1]))

        try :
            ciphertext = make_password(cleartext, self.fixed_field, self.type)
            # ciphertext = self._remove_prefix(ciphertext)
            self.logger.info('密码加密成功')
            return (True, ciphertext)
        except Exception as e:
            self.logger.error('密码加密失败，原因：' + str(e))
            return (False, '加密失败，' + str(e))
    
    
    def verify(self, cleartext, ciphertext):
        
        '''
        验证密码，用于明文密码和加密密码是否配对
        :parm
            cleartext：明文密码
            ciphertext：加密密码
        '''
        
        if not cleartext :
            self.logger.error('验证密码失败，原因：参数cleartext不能为空')
            return False
        
        result = self.encryt(cleartext, is_validate=False)
        if not result[0] :
            self.logger.error('验证密码失败，原因：' + result[1])
            return result
        else :
            new_ciphertext = result[1]
        
        if ciphertext == new_ciphertext :
            self.logger.info('验证密码成功，密码匹配')
            return True
        else :
            self.logger.warn('验证密码成功，密码不匹配')
            return False


    def _remove_prefix(self, data):
        '''
        去掉前缀
        '''
        temp_list = re.split('\$' , data) 
        replace_str = temp_list[0] + '$' + temp_list[1] + '$' + temp_list[2] + '$'
        return data.replace(replace_str , '')
        

    def _validate(self, data):
        
        '''
        验证密码复杂度
        '''
        if not isinstance(data, str) or not data : 
            self.logger.error('验证密码复杂度失败，原因：参数data必须是非空字符串')
            return (False, '参数data必须是非空字符串')
        
        if len(data) < self.min_len :
            # 长度必须大于最小长度
            self.logger.error('验证密码复杂度失败，原因：密码长度必须大于' + str(self.min_len) + '位')
            return (False, '长度不够')
        # elif not (re.search('[a-z]{1,}' , data) and re.search('[0-9]{1,}' , data) and re.search('[A-Z]{1,}' , data)):
        elif not (re.search('[a-z]{1,}' , data) and re.search('[0-9]{1,}' , data)):
            self.logger.error('验证密码复杂度失败，原因：复杂度不够，必须是数字和字母组合')
            return (False, '复杂度不够，必须是数字和字母组合')
            return (False, '复杂度不够，必须是数字、大小写组合')
    
        return (True, '')
