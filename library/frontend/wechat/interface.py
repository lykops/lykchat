from library.frontend.wechat import Wechat_Base
from library.frontend.wechat.single import Manager_Single
from library.utils.type_conv import bytes2string

class Manager_Interface(Wechat_Base):
    def sendmsg(self, ifpwd, tousername, content, wxid=None, filename='', post_field='UserName'):
        
        '''
        信息发送接口
        可以为get、post方法
        参数含义：
            fromalias：发送者的微信号，目前没有使用该参数
            friendfield：接受者的字段代号，{0:'NickName' , 1:'Alias' , 2:'RemarkName'} 
            friend：接受者信息
            content：发送内容
        /sendmsg?friendfield=1&friend=lykops724&content=不要
        '''
        
        if ifpwd != 'I come from website!!!!' :
            result = self.verify_ifpwd(ifpwd)
            if not result[0] :
                return result
        
        result = self.get_abs(force=True)
        if result[0] :
            abs_list = result[1]
        else :
            return (False, '获取登陆微信列表错误')
        
        report_dict = {
            'ok':{},
            'ng':{}
            }
        
        for session_dict in abs_list :
            self.logger.info(session_dict)
            try :
                uuid = session_dict.get('uuid', None)
            except :
                uuid = None
            status = session_dict.get('status', 100)
            
            if status == 222 :
                nickname = session_dict['nickname']
                if wxid is None or not wxid:
                    single_api = Manager_Single(self.username, uuid=uuid, redisclient=self.redisclient)
                    result = single_api.send_msg(tousername, content, caller='interface' , filename=filename, post_field=post_field)
                    if result[0] :
                        if result[1]['text']['ok'] :
                            # report_dict['ok'][nickname] = result[1]
                            report_dict['ok'] = result[1]
                            return (True, report_dict)
                        else :
                            report_dict['ng'][nickname] = result[1]
                    else :
                        report_dict['ng'][nickname] = result[1]
                else :
                    if wxid == nickname :
                        single_api = Manager_Single(self.username, uuid=uuid, redisclient=self.redisclient)
                        result = single_api.send_msg(tousername, content, caller='interface' , filename=filename, post_field=post_field)
                        if result[0] :
                            # report_dict['ok'][nickname] = result[1]
                            report_dict['ok'] = result[1]
                            return (True, report_dict)
                        else :
                            report_dict['ng'][nickname] = result[1]
                            return (False, report_dict)
                    
        return (False, report_dict)
                
    
    def check_login(self, ifpwd='', uuid=None):
        
        if ifpwd != 'I am crontab!!!!' :
            result = self.verify_ifpwd(ifpwd)
            if not result[0] :
                return result
        
        result = self.get_abs(force=True)
        if result[0] :
            abs_list = result[1]
        else :
            return (False, {})

        report_dict = {}
        for uuid_info in abs_list :
            new_uuid = uuid_info.get('uuid', None)
            status = uuid_info.get('status', 100)
            
            if uuid is not None and uuid != new_uuid :
                continue
                
            if status == 222 :
                single_api = Manager_Single(self.username, uuid=new_uuid, redisclient=self.redisclient)
                result = single_api.check_login()
                report_dict[new_uuid] = {}
                if result[0] :
                    report_dict[new_uuid]['code'] = int(result[1])
                    session_dict = result[2]
                    report_dict[new_uuid]['status'] = session_dict.get('status', 100)
                    report_dict[new_uuid]['logout_timestamp'] = session_dict.get('logout_timestamp', '')
                    report_dict[new_uuid]['logint_timestamp'] = session_dict.get('logint_timestamp', '')
                    report_dict[new_uuid]['nickname'] = session_dict.get('nickname', '')
                    report_dict[new_uuid]['alias'] = session_dict.get('alias', '')
                    report_dict[new_uuid]['logint_timestamp'] = session_dict.get('logint_timestamp', '')
                    report_dict[new_uuid]['now_stamptime'] = session_dict.get('now_stamptime', '')
                
            if uuid is not None and uuid == new_uuid :
                break
                    
        return (True, report_dict)
    
    
    def check_alluser(self, ipaddr):
        
        if not (ipaddr == '127.0.0.1' or ipaddr == 'localhost'):
            return (False, '只允许本地访问')
        
        rdskey_prefix = 'lykchat:*:wechat:session:*'
        result = self.redisclient.getkey(rdskey_prefix)
        if result[0] :
            rdskey_list = result[1]
        else :
            rdskey_list = []

        user_list = []
        for rdskey in rdskey_list :
            rdskey = bytes2string(rdskey)
            user = rdskey.split(':')[1]
            user_list.append(user)
            
        user_list = list(set(user_list))
        
        report_dict = {}
        for username in user_list :
            interface_api = Manager_Interface(username, redisclient=self.redisclient)
            result = interface_api.check_login(ifpwd='I am crontab!!!!')
            self.logger.info(result)
            if result[0] :
                report_dict[username] = result[1]
            else :
                report_dict[username] = '检查失败，原因：' + result[1]
                
        return (True, report_dict)
               
