import time, os

from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls.base import reverse
from pip._vendor.requests.sessions import session

from library.config import wechat
from library.wechat.friend import Get_Friend
from library.wechat.login import Login
from library.wechat.logout import Logout
from library.wechat.ready import Ready
from library.wechat.send import Send_Msg
from lykchat.settings import BASE_DIR


class Login_Wechat(): 
    def __init__(self):
        self.session_field_list = wechat.session_field_list
        self.is_text = False
        self.display_html = 'wechat.html'
        self.session_type = wechat.session_type
        

    def _init_param(self, request):
        op_session = Operate_Session()
        self.session_info_dict = op_session.get_info(request)

        try : 
            status = self.session_info_dict['status']
            if status :
                status = int(status)
            else :
                status = 100
        except :
            status = 100
        self.status = status
    
        self.uuid = self._return_info_key('uuid')
        self.redirect_uri = self._return_info_key('redirect_uri')
        self.login_info = self._return_info_key('login_info')
        self.web_request_base_dict = self._return_info_key('web_request_base_dict')
        self.login_stamptime = self._return_info_key('login_stamptime')
        self.qr_stamptime = self._return_info_key('qr_stamptime')
        self.change_stamptime = self._return_info_key('change_stamptime')
        self.Alias = self._return_info_key('Alias')
        self.NickName = self._return_info_key('NickName')
        self.qr_url = self._return_info_key('qr_url')


    def _return_info_key(self, key):
        try : 
            if self.status == 100 or self.status > 400 :
                return False
            else :
                return self.session_info_dict[key]
        except :
            return False


    def lykchat(self, request):
        '''
        web页面，路由功能
        '''
        self._init_param(request)
        if self.status < 200:
            return self._step_getqr(request)
        elif self.status > 200 and self.status < 222:
            return self._step_confirm(request)
        elif self.status == 222:
            return self._step_checklogin(request)
        elif self.status == 200:
            return self._step_login(request)
        elif self.status >= 400 and self.status < 500:
            return self._step_getqr(request)
        else :
            return self._step_getqr(request)


    def logout(self, request):
        self._init_param(request)
        if self.status == 222 :
            wx_logout = Logout(self.web_request_base_dict, self.login_info)
            wx_logout.logout()
            self.session_info_dict['status'] = self.status = 444
            display_html_dict = self._displayhtml(request)
            return render(request, self.display_html, display_html_dict) 
        else :
            return HttpResponseRedirect(reverse('index'))


    def interface_sendmsg(self, request):
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
        parameter_dict = {
            'fromalias':'发送者的微信号，目前没有使用该参数',
            'friendfield':'接受者的字段代号，{0:"NickName" , 1:"Alias" , 2:"RemarkName"}，可以为空，默认为0 ',
            'friend':'接受者的昵称、别名、备注名的其中一个，不能为空',
            'content':'发送内容，不能为空',
        }
        send_result = {}
        self._init_param(request)
        request_dict = {}
        if self.status != 222 :
            send_result = {'retcode': 1101 , 'errmsg' : '微信还未登录或者退出登录' }

        key_list = ['fromalias', 'friendfield', 'friend', 'content']        
        if request.method == 'GET' :
            for key in key_list :
                try :
                    request_dict[key] = request.GET[key]
                except :
                    if key == 'friend' :
                        send_result = {'ResultCode':-1005 , 'ErrMsg' : '接受者不能为空', 'parameter_dict' : parameter_dict}
                    else :
                        request_dict[key] = False
        else :
            for key in key_list :
                try :
                    request_dict[key] = request.POST[key]
                except :
                    if key == 'friend' :
                        send_result = {'ResultCode':-1005 , 'ErrMsg' : '接受者不能为空', 'parameter_dict' : parameter_dict}
                        request_dict[key] = 'filehelper'
                    else :
                        request_dict[key] = False
        
        if request_dict['content'] == '' or not request_dict['content'] :
            send_result = {'ResultCode':-1005 , 'ErrMsg' : '内容不能为空', 'parameter_dict' : parameter_dict}

        friendfield_dict = {0:'NickName' , 1:'Alias' , 2:'RemarkName'}   
        
        try :     
            if request_dict['friend'] == 'filehelper' :
                tousername = 'filehelper'
                friendfield = 'NickName'
            else :
                tousername = request_dict['friend']
                fieldindex = int(request_dict['friendfield'])
                if fieldindex not in friendfield_dict:
                    friendfield = 'NickName'
                else :
                    friendfield = friendfield_dict[fieldindex]       
                           
            nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())  
            # content = 'lykchat 发送接口推送：' + request_dict['content']
            content = nowtime + '\n' + request_dict['content']
        except :
            send_result = {'ResultCode':-1005 , 'ErrMsg' : '参数错误', 'parameter_dict' : parameter_dict}

        if send_result == {} or not send_result :
            send_result = self._send_msg(tousername=tousername , content=content , call_type='interface', post_field=friendfield)
        return render(request, 'result.html', {'send_result':send_result}) 


    def _step_getqr(self, request):
        '''
        初始化，获取uuid、cookies、session、二维码等等
        '''
        if (not self.uuid or self.uuid == '') or (self.web_request_base_dict == {} or not self.web_request_base_dict):
            wx_ready = Ready(is_text=self.is_text)
            (self.uuid, self.web_request_base_dict) = wx_ready.return_basicinfo_dict()
        else :
            wx_ready = Ready(uuid=self.uuid, web_request_base_dict=self.web_request_base_dict, is_text=self.is_text)
    
        self.qr_file = wechat.qr_dir + '/' + self.uuid + '.jpg'
        if not os.path.exists(self.qr_file) or not os.path.isfile(self.qr_file) :
            self.qr_file = wx_ready.get_qr()
        
        self.qr_url = self.qr_file.replace(BASE_DIR, '')
        (self.uuid, self.web_request_base_dict) = wx_ready.return_basicinfo_dict()
        self.status = 202
    
        self.session_info_dict['uuid'] = self.uuid
        self.session_info_dict['web_request_base_dict'] = self.web_request_base_dict
        self.session_info_dict['status'] = self.status
        self.session_info_dict['qr_url'] = self.qr_url
        self.session_info_dict['qr_stamptime'] = int(time.time())
        
        display_html_dict = self._displayhtml(request)
        return render(request, self.display_html, display_html_dict)
    
    
    def _step_confirm(self, request):
        '''
        检查是否扫描和确认登陆
        '''
        count = 0
        while 1:
            wx_ready = Ready(uuid=self.uuid, web_request_base_dict=self.web_request_base_dict, is_text=self.is_text)
            (self.status, self.redirect_uri) = wx_ready.check_status()
            self.session_info_dict['status'] = self.status
            self.session_info_dict['redirect_uri'] = self.redirect_uri
            print(self.status)
            if self.status == 200 or self.status >= 400 :
                break
                
            if count == 5 :
                break
            count += 1
            
        if self.status == 200 :
            self._login(request)

        display_html_dict = self._displayhtml(request)
        return render(request, self.display_html, display_html_dict) 
    
    
    def _step_login(self, request):
        '''
        确认登陆之后，进行登陆
        '''
        self._login(request)
        display_html_dict = self._displayhtml(request)
        return render(request, self.display_html, display_html_dict) 


    def _login(self, request):
        '''
        确认登陆之后，进行登陆
        '''
        count = 0
        while 1 :
            if self.login_info == {} or not self.login_info:
                wx_login = Login(self.web_request_base_dict, redirect_uri=self.redirect_uri, is_text=self.is_text)
                self.login_info = wx_login.get_logininfo()
                self.status = 200
            else :
                self.status = self._check_login(request)
            print(self.status)
    
            if self.status == 222 or self.status >= 400 :
                if self.status == 222 :
                    self.friend_dict = self._get_friend_dict()
                    self.session_info_dict['login_stamptime'] = int(time.time())
                break
            else :
                time.sleep(5)
                
            if count == 5 :
                break
            count += 1
    
        self.session_info_dict['status'] = self.status
        self.session_info_dict['login_info'] = self.login_info

    
    def _step_checklogin(self, request):
        '''
        检查登陆状态
        '''
        self.status = self._check_login(request)
        self.friend_dict = self._get_friend_dict()
        if request.method == 'POST' :
            try :
                tousername = request.POST['username']
                try : 
                    # nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    content = request.POST['content']
                    content = 'lykchat web页面推送：' + content
                    self.send_result = self._send_msg(tousername, content)
                except :
                    self.send_result = '<div class="alert alert-danger text-center">发送内容为空</div>'
            except :
                self.send_result = '<div class="alert alert-danger text-center">发送内容为空</div>'
        else :
            self.send_result = ''

        self.session_info_dict['status'] = self.status
        display_html_dict = self._displayhtml(request)
        return render(request, self.display_html, display_html_dict) 
    

    def _check_login(self, request):
        '''
        检查是否保持登陆状态
        '''
        wx_login = Login(self.web_request_base_dict, login_info=self.login_info, is_text=self.is_text)
        status_dict = wx_login.check_login()
        status = status_dict['Ret']
        if status == 0 :
            status = 222
            # 登陆成功状态
        elif status == 1101 :
            status = 402
        elif status == 1205 :
            status = 404
        else :
            status = 401
    
        return status

    
    def _displayhtml(self, request):
        '''
        页面渲染
        '''
        from library.config.wechat import login_status_code_dict
        display_html_dict = login_status_code_dict[self.status]
        if self.login_stamptime and self.login_stamptime != '' :
            login_min = (int(time.time()) - int(self.login_stamptime)) // 60
        else :
            login_min = 0
        if login_min > 60 * 24 * 7 :
            login_min = 0  
        if login_min>=60 :
            login_min = str(login_min // 60) + '小时' + str(login_min % 60) + '分钟'
        else :
            login_min = str(login_min) + '分钟'
        display_html_dict['login_min'] = login_min
        
        for session_field in self.session_field_list :
            try :
                display_html_dict[session_field] = self.session_info_dict[session_field]
            except :
                display_html_dict[session_field] = ''
        
        display_html_dict['nowtime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        
        try :
            display_html_dict['friend_dict'] = self.friend_dict
        except :
            display_html_dict['friend_dict'] = {}
        
        try :
            display_html_dict['send_result'] = self.send_result
        except :
            display_html_dict['send_result'] = ''

        op_session = Operate_Session()
        op_session.update(request, self.session_info_dict)

        return display_html_dict

    
    def _get_friend_dict(self):
        # 好友列表不能被缓存，否则登陆久了无法发送信息
        get_friend = Get_Friend(self.login_info, self.web_request_base_dict)
        friend_list = get_friend.get_friend_list()
        friend_dict = get_friend.get_friend_dict(friend_list=friend_list)
        self.session_info_dict['nickname'] = friend_list['NickName'][0]
        self.session_info_dict['alias'] = friend_list['Alias'][0]
        return friend_dict
        

    def _send_msg(self , tousername, content, call_type='' , post_field='UserName'):
        '''
        发送信息，处理返回值
        '''
        send_msg = Send_Msg(self.login_info, self.web_request_base_dict)
        send_result_dict = send_msg.send(content, tousername=tousername, post_field=post_field)

        if send_result_dict['ResultCode'] == -1 :
            self.status = 402

        if call_type == 'interface' :
            return send_result_dict

        if send_result_dict['ResultCode'] == 0 :
            send_result = '信息：' + content + '</br>发送给' + str(send_result_dict['friend_dict']) + '</br>成功发送'
            return '<div class="alert alert-success text-center">' + send_result + '</div>'
        else :
            send_result = '信息：' + content + '</br>发送给' + str(send_result_dict['friend_dict']) + '</br>结果为' + send_result_dict['ErrMsg'] + '</br>返回原文为' + str(send_result_dict)
            return '<div class="alert alert-danger text-center">' + send_result + '</div>'
        

class Operate_Session():
    def __init__(self):
        self.session_field_list = wechat.session_field_list
        self.is_text = False
        self.display_html = 'wechat.html'
        self.session_type = wechat.session_type


    def update(self, request, info_dict):
        '''
        更新的session，如果状态退出，设置为空
        '''
        is_change = 0
        status = info_dict['status']
        print(status)
        if status < 300 :
            for session_field in self.session_field_list :
                try :
                    # if request.session[session_field] != info_dict[session_field] :
                    # 不能用这个if，导致刷新页面无法获得会话值
                    request.session[session_field] = info_dict[session_field]
                    is_change = 1
                except:
                    if session_field == 'type' :
                        request.session[session_field] = self.session_type
                    else :
                        # request.session[session_field] = ''
                        try :
                            del request.session[session_field]
                        except :
                            pass
                    is_change = 1
                
            if is_change == 1 or self.status == 222:
                request.session['change_stamptime'] = int(time.time())
        else :
            self._clear_expire(request)

        return ''


    def get_info(self, request):
        '''
        获取微信登陆信息
        '''
        uuid = self._get_current_key(request, 'uuid')
        status = self._get_current_key(request, 'status')
        if status == False :
            status = 100
        else :
            status = int(status)

        info_dict = {}
        history_info = self._get_history_newest(uuid=uuid)
        if (not uuid or uuid == False):
            # 该session没有登陆过,去查找历史session
            if history_info != {} :
                info_dict = history_info
            else :
                info_dict = {}
        else :     
            # 登陆成功、扫码之后等状态使用自己的会话；非登陆成功的使用历史会话
            if status == 222 or status == 201 or status == 200:
                for session_field in self.session_field_list : 
                    info_dict[session_field] = self._get_current_key(request, session_field)
            elif status >= 300:
                info_dict = {}
                # 退出登录，字典为空
            else :
                for session_field in self.session_field_list :
                    try :
                        info_dict[session_field] = history_info[session_field]
                    except :
                        info_dict[session_field] = False
                    
        session_status = self._check_timeout(request, info_dict)
        if not session_status :
            info_dict = {}
                    
        return info_dict
    
    
    def _get_current_key(self, request, key):
        '''
        获取用户请求session的键值
        '''
        try :
            return request.session[key]
        except :
            return False


    def _clear_expire(self, request):
        '''
        清理过期回话信息
        '''
        # uuid = session_info_dict['uuid']
        # currency_session_key = request.session.session_key
        # 删除掉指定uuid的历史回话（除自己外），注意：在清理回话时不能删除自己的回话，否则页面报错
        # if uuid and uuid != '' :
        if 1 :
            from django.contrib.sessions.models import Session
            import datetime
            online_sessions = Session.objects.filter(expire_date__gte=datetime.datetime.now())
            for session in online_sessions :
                # 这里的session不要改名，否则报错
                try :
                    history_session_info = session.get_decoded()
                    '''
                    if str(session) == str(currency_session_key):
                        # 在清理回话时不能删除自己的回话，否则页面报错，需要把这两个字符串化
                        request.session.set_expiry(1) 
                        # 设置超时
                    '''
                    
                    if history_session_info['type'] == 'web_wechat_login': 
                        request.session.set_expiry(1) 
                        # 设置超时
                        # Session.objects.get(session_key=session).delete() 
                except Exception as e:
                    print(e)
                    pass


    def _check_timeout(self, request, info_dict):
        '''
        检查回话是否可用
        二维码生成之后只能在规定时间内扫描，否则超时
        '''
        if info_dict == {} or not info_dict:
            return False
        
        try :
            status = info_dict['status']
            qr_stamptime = info_dict['qr_stamptime']
        except :
            return False
    
        if status < 200 or status == 202 :
            qr_second = int(time.time()) - int(qr_stamptime)
            if qr_second > 180 :
                return False
            else :
                return True
        elif status >= 300 :
            return False
        else :
            return True
    
    
    def _get_history_newest(self, uuid=''):
        '''
        获取最新的历史session信息
        '''
        from django.contrib.sessions.models import Session
        import datetime
        online_sessions = Session.objects.filter(expire_date__gte=datetime.datetime.now()) 
        # 获取未过期的sessions
        
        change_stamptime_list = []
        history_session_list = []
        for session in online_sessions :
            # 这里的session不要改名，否则报错
            history_session_info = session.get_decoded()
    
            try :
                old_type = history_session_info['type']
                if old_type != 'web_wechat_login' :
                    break
                
                old_uuid = history_session_info['uuid']
                if (uuid != '' and uuid) and uuid != old_uuid :
                    break
    
                change_stamptime = history_session_info['change_stamptime']
                change_stamptime = int(change_stamptime)
                
                change_stamptime_list.append(change_stamptime)
                history_session_list.append(history_session_info)
            except :
                pass
        
        try :
            last_changetime = max(change_stamptime_list)
            # 获取最新更新时间
            index_no = change_stamptime_list.index(last_changetime)
            return history_session_list[index_no]
        except :
            return {}
     
