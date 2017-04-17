from fileinput import filename
import time

from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls.base import reverse
from pip._vendor.requests.sessions import session

from library.config import wechat
from library.keepalive.wechat.logininfo import Manage_Logininfo
from library.wechat.friend import Get_Friend
from library.wechat.login import Login
from library.wechat.logout import Logout
from library.wechat.ready import Ready
from library.wechat.send import Send_Msg


class Base():
    def __init__(self):
        self.display_html = 'wechat.html'
        self.user_mess_dict = wechat.user_mess_dict
        

    def _get_friend_info(self):  
        '''
        获取登陆之后的好友等信息
        '''
        try :
            change_timestamp = int(self.session_info_dict['change_timestamp'])
        except :
            change_timestamp = 0
        
        self.friend_dict = self.session_info_dict['friend_dict']
        self.friend_list = self.session_info_dict['friend_list']
        change_time = int(time.time()) - change_timestamp
           
        get_friend = Get_Friend(self.session_info_dict) 
        if (self.friend_dict != {} and self.friend_dict) or self.friend_list != {'UserName': [], 'NickName': [], 'Alias': [], 'Sex': [], 'RemarkName': []} :
            if change_time >= 3600:
                self.session_info_dict = get_friend.get_friend_list()
        else :
            self.session_info_dict = get_friend.get_friend_list()

        self.session_info_dict = get_friend.update_friend_list()
        self.session_info_dict = get_friend.get_friend_dict()
 

    def _send_msg(self , tousername, content, filename='', msgType='txt', call_type='' , post_field='UserName'):
        '''
        发送信息，处理返回值
        '''
        send_msg = Send_Msg(self.session_info_dict)
        send_result_dict = send_msg.send(content, msgType=msgType, filename=filename, tousername=tousername, post_field=post_field)

        if send_result_dict['Code'] == -1 :
            self.status = 402

        if call_type == 'interface' :
            return send_result_dict

        if send_result_dict['Code'] == 0 :
            send_result = '成功发送'
            return '<div class="alert alert-success text-center">' + send_result + '</div>'
        else :
            send_result = '成功失败'
            return '<div class="alert alert-danger text-center">' + send_result + '</div>'


class Interface(Base):
    def sendmsg(self, request):
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
            'username' : '用户' ,
            'pwd' : '接口密码，注意不等于登陆密码' ,
            'type' : '发送信息类型，{"txt":"纯文字" ,"img":"图片","file":"发送文件","video":"视频"}，可以为空，默认：没有文件为txt，有文件为file',
            'fromalias':'发送者的微信号，目前没有使用该参数',
            'friendfield':'接受者的字段代号，{0:"NickName" , 1:"Alias" , 2:"RemarkName"}，可以为空，默认为0',
            'friend':'接受者的昵称、微信号、备注名的其中一个，不能为空',
            'content':'发送内容，不能为空',
            'get方法测试url' : 'sendmsg?username=zabbix&pwd=123456&type=txt&friendfield=1&friend=lyk-ops&content=test'
        }
        # curl -F "file=@/root/a" 'http://127.0.0.1/sendmsg?username=zabbix&pwd=123456&type=img&friendfield=1&friend=lyk-ops&content=test'
        friendfield_dict = {0:'NickName' , 1:'Alias' , 2:'RemarkName'} 
        resultpage = 'result.html'
        request_dict = {}
        send_result = {}
        
        for key in ['username', 'pwd', 'friend', 'content'] :
            try :
                try:
                    request_dict[key] = request.GET[key]
                except :
                    request_dict[key] = request.POST[key]
            except :
                send_result = {'Code':-1101 , 'Msg' : '缺少必要的参数', 'ErrMsg' : parameter_dict}
                return render(request, resultpage, {'result':send_result}) 

        # 验证用户的接口密码是否正确
        username = request_dict['username']
        pwd = request_dict['pwd']
        password = wechat.user_mess_dict[username]['interface_pwd']
        if pwd != password :
            send_result = {'Code':-1101 , 'Msg' : str(username) + '接口密码错误，请注意不等于登陆密码', 'ErrMsg' : parameter_dict}
            return render(request, resultpage, {'result':send_result}) 
        
        op_info = Manage_Logininfo()
        self.session_info_dict = op_info.get_info(username)
        status = self.session_info_dict['status']
        if status != 222 :
            # 验证登陆情况
            send_result = {'Code': 1101 , 'Msg' : '微信还未登录或者退出登录', 'ErrMsg' : '' }
            return render(request, resultpage, {'result':send_result}) 

        for key in ['type', 'friendfield'] :
            try :
                try:
                    request_dict[key] = request.GET[key]
                except :
                    request_dict[key] = request.POST[key]
            except :
                if key == 'type' :
                    request_dict[key] = 'txt'
                if key == 'friendfield' :  
                    request_dict[key] = 0

        if request_dict['type'] not in ['txt', 'img', 'file', 'video'] :
            request_dict['type'] = 'txt'
        
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
                            
        try :
            file = request.FILES['file']
            if file.size > wechat.max_upload_size:
                send_result = {
                    'status' : '上传文件超过最大值',
                    'file_uuid':'',
                }
                return render(request, 'result.html', {'result':send_result}) 
        
            request_dict['type'] = 'file'
            from library.file.upload import upload_file
            filename = str(file)
            filename = upload_file(file, filename=filename , username=username)
        except :
            filename = ''
            request_dict['type'] = 'txt'
        
        # nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())  
        # content = 'lykchat 发送接口推送：' + request_dict['content']
        # content = nowtime + '\n' + request_dict['content']
        content = request_dict['content']
        send_result = self._send_msg(tousername=tousername , content=content , msgType=request_dict['type'] , filename=filename, call_type='interface', post_field=friendfield)
        return render(request, resultpage, {'result':send_result}) 

    
    def check_login(self, request):
        '''
        检查所有微信号登陆状态
        '''
        request_dict = {}
        for key in ['username' , 'pwd'] :
            # post或者get字段是否正确
            try :
                if request.method == 'GET' :
                    request_dict[key] = request.GET[key]
                else :
                    request_dict[key] = request.POST[key]
            except :
                send_result = '账号或者密码不能为空'

        try :
            # 验证用户的接口密码是否正确
            username = request_dict['username']
            pwd = request_dict['pwd']
            password = self.user_mess_dict[username]['interface_pwd']
            
            if pwd != password :
                send_result = {
                    'username' : username ,
                    'check_time' : int(time.time()),
                    'login_time' : '',
                    'login_min' : '',
                    'alias' : '',
                    'nickname' : '',
                    'longtime' : '0',
                    'status' : '账号或者密码错误'
                    }
            else :
                send_result = {}
        except :
            send_result = {
                'username' : '' ,
                'check_time' : int(time.time()),
                'login_min' : '',
                'login_time' : '',
                'alias' : '',
                'nickname' : '',
                'status' : '账号或者密码错误'
                }
        
        if send_result == {} :
            from library.config.wechat import login_status_code_dict
            op_info = Manage_Logininfo()
            session_info_dict = op_info.get_info(username)
            status = session_info_dict['status']
            if status == 222 :
                wx_login = Login(session_info_dict)
                session_info_dict = wx_login.check_login()
                status = session_info_dict['status']
                
                op_info.update(session_info_dict)
                request.session['username'] = username

                login_stamptime = session_info_dict['login_stamptime']
                if login_stamptime and login_stamptime != '' :
                    login_min = (int(time.time()) - int(login_stamptime)) // 60
                else :
                    login_min = 0
                if login_min > 60 * 24 * 365 :
                    login_min = 0  
                    
                if login_min >= 60 * 24 :
                    login_min = str(login_min // 60 // 24) + '天' + str(login_min // 60 % 24) + '小时' + str(login_min % 60) + '分钟'
                elif login_min >= 60 :
                    login_min = str(login_min // 60) + '小时' + str(login_min % 60) + '分钟'
                else :
                    login_min = str(login_min) + '分钟'

                send_result = {
                    'username' : username ,
                    'check_time' : int(time.time()),
                    'login_time' : session_info_dict['login_stamptime'],
                    'login_min' : login_min,
                    'alias' : session_info_dict['myself']['Alias'],
                    'nickname' : session_info_dict['myself']['NickName'],
                    'status' : login_status_code_dict[status]['descript']
                    }
            else :
                send_result = {
                    'username' : username ,
                    'check_time' : int(time.time()),
                    'login_min' : '',
                    'login_time' : '',
                    'alias' : '',
                    'nickname' : '',
                    'status' : login_status_code_dict[status]['descript']
                    }
                
        return render(request, 'result.html', {'result':send_result}) 
    

class Manage(Base): 
    def login(self, request):
        # 用户登录页面
        from .forms import Form_Login
        if request.method == 'GET' :
            is_login = self._check_userlogin(request)
            if is_login :
                return HttpResponseRedirect(reverse('index'))
            else :
                form = Form_Login()
                return render(request, 'login.html', {'form': form})
        else:
            form = Form_Login(request.POST)
            if form.is_valid():
                post_username = request.POST.get('username')
                post_password = request.POST.get('password')
                error_message = False

                try :
                    password = self.user_mess_dict[post_username]['login_pwd']
                except :
                    error_message = '登陆失败：用户名错误'
                    return render(request, 'login.html', {'form': form, 'error_message':error_message})
                    
                if password != post_password :
                    error_message = '登陆失败：密码错误'
                    return render(request, 'login.html', {'form': form, 'error_message':error_message})
                else :
                    request.session['username'] = post_username
                    return HttpResponseRedirect(request.session.get('pre_url', reverse('index')))
                
                
    def index(self, request):
        '''
        web页面，路由功能
        '''
        is_login = self._check_userlogin(request)
        if not is_login :
            return HttpResponseRedirect(reverse('login'))
        
        self._init_param(request)
        self.session_info_dict['username'] = request.session['username']
        
        if self.status < 200:
            self._getqr(request)
        elif self.status > 200 and self.status < 222:
            self._confirm(request)
        elif self.status == 222:
            self._checklogin(request)
        elif self.status == 200 or self.status == 221:
            self._init(request)
        else :
            self._getqr(request)

        display_html_dict = self._displayhtml(request)
        return render(request, self.display_html, display_html_dict) 


    def wx_logout(self, request):
        '''
        用于微信退出
        '''
        is_login = self._check_userlogin(request)
        if not is_login :
            return HttpResponseRedirect(reverse('login'))
        
        self._init_param(request)
        if self.status == 222 :
            wx_logout = Logout(self.session_info_dict)
            wx_logout.logout()
            self.session_info_dict['status'] = self.status = 444
            display_html_dict = self._displayhtml(request)
            return render(request, self.display_html, display_html_dict) 
        else :
            return HttpResponseRedirect(reverse('index'))


    def logout(self, request):
        '''
        退出登录，也就是切换用户，但不退出现有微信号
        '''
        from django.contrib import auth
        auth.logout(request)
        return HttpResponseRedirect(reverse('login'))


    def _getqr(self, request):
        '''
        初始化，获取uuid、cookies、session、二维码等等
        '''
        wx_ready = Ready(self.session_info_dict)
        self.session_info_dict = wx_ready.get_qr()


    def _confirm(self, request):
        '''
        检查是否扫描和确认登陆
        '''
        count = 0
        while 1:
            wx_ready = Ready(self.session_info_dict)
            self.session_info_dict = wx_ready.check_status()
            status = self.session_info_dict['status']
            if (status == 200 or status >= 400) or count == 5 :
                break
            count += 1
            
        if status == 200 :
            self._init(request)

    
    def _init(self, request):
        '''
        确认登陆之后，进行登陆
        '''
        count = 0
        while 1 :
            self.login_info = self.session_info_dict['login_info']
            if self.login_info == {} or not self.login_info:
                wx_login = Login(self.session_info_dict)
                self.session_info_dict = wx_login.init_login()
            else :
                wx_login = Login(self.session_info_dict)
                self.session_info_dict = wx_login.check_login()

            status = self.session_info_dict['status']
            if status == 222 or self.status >= 400 or count == 5 :
                if status == 222 :
                    self._get_friend_info()
                    self.session_info_dict['login_stamptime'] = int(time.time())
                break
            else :
                time.sleep(5)

            count += 1

    
    def _checklogin(self, request):
        '''
        检查登陆状态
        '''
        wx_login = Login(self.session_info_dict)
        self.session_info_dict = wx_login.check_login()
        status = self.session_info_dict['status']

        if status == 222 :
            self._get_friend_info()
            if request.method == 'POST' :
                try :
                    tousername = request.POST['username']
                    
                    try :
                        file = request.FILES['file']
                        if file.size > wechat.max_upload_size:
                            filename = False
                        else :
                            from library.file.upload import upload_file
                            filename = str(file)
                            filename = upload_file(file, filename=filename , username='zabbix')
                    except :
                        filename = False
                    
                    try : 
                        # nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                        content = request.POST['content']
                        content = 'lykchat web页面推送：' + content
                        
                        if not filename :
                            self.send_result = self._send_msg(tousername, content)
                        else :
                            self.send_result = self._send_msg(tousername, content, filename=filename, msgType='file') 
                    except :
                        self.send_result = '<div class="alert alert-danger text-center">发送内容为空</div>'
                except :
                    self.send_result = '<div class="alert alert-danger text-center">发送内容为空</div>'
            else :
                self.send_result = ''


    def _displayhtml(self, request):
        '''
        页面渲染
        '''
        from library.config.wechat import login_status_code_dict
        status = self.session_info_dict['status']
        display_html_dict = login_status_code_dict[status]
        login_stamptime = self.session_info_dict['login_stamptime']
        if login_stamptime and login_stamptime != '' :
            login_min = (int(time.time()) - int(login_stamptime)) // 60
        else :
            login_min = 0
        if login_min > 60 * 24 * 365 :
            login_min = 0  
            
        if login_min >= 60 * 24 :
            login_min = str(login_min // 60 // 24) + '天' + str(login_min // 60 % 24) + '小时' + str(login_min % 60) + '分钟'
        elif login_min >= 60 :
            login_min = str(login_min // 60) + '小时' + str(login_min % 60) + '分钟'
        else :
            login_min = str(login_min) + '分钟'
        display_html_dict['login_min'] = login_min
        display_html_dict['nowtime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        display_html_dict['username'] = self.session_info_dict['username']
        display_html_dict['qr_url'] = self.session_info_dict['qr_url']
        display_html_dict['status'] = self.session_info_dict['status']
        display_html_dict['uuid'] = self.session_info_dict['uuid']
        display_html_dict['version'] = wechat.version
        
        try :
            display_html_dict['nickname'] = self.session_info_dict['myself']['NickName']
            display_html_dict['alias'] = self.session_info_dict['myself']['Alias']
        except :
            display_html_dict['nickname'] = ''
            display_html_dict['alias'] = ''
        
        try :
            display_html_dict['friend_dict'] = self.session_info_dict['friend_dict']
        except :
            display_html_dict['friend_dict'] = {}
        
        try :
            display_html_dict['send_result'] = self.send_result
        except :
            display_html_dict['send_result'] = ''
            
        op_info = Manage_Logininfo()
        op_info.update(self.session_info_dict)
        request.session['username'] = self.username
        
        return display_html_dict


    def _check_userlogin(self, request):
        '''
        检查之前是否登录，username为session的用户
        '''
        try :
            self.username = request.session['username']
        except :
            return False
            
        from django.contrib.sessions.models import Session
        import datetime
        online_sessions = Session.objects.filter(expire_date__gte=datetime.datetime.now()) 
        # 获取未过期的sessions
        
        for session in online_sessions :
            session_dict = session.get_decoded()
            if self.username == session_dict['username'] :
                return True
        return False


    def _init_param(self, request):
        op_info = Manage_Logininfo()
        self.session_info_dict = op_info.get_info(self.username)

        self.status = self.session_info_dict['status']
        self.web_request_base_dict = self.session_info_dict['web_request_base_dict']
        self.friend_dict = self.session_info_dict['friend_dict']
        self.friend_list = self.session_info_dict['friend_list']
