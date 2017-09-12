import logging

from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls.base import reverse

from library.config.frontend import adminuser
from library.frontend.sysadmin.uri import Manager_Uri
from library.frontend.sysadmin.user import Manager_User
from library.storage.database.mongo import Op_Mongo
from library.storage.database.redis_api import Op_Redis
from library.storage.logging.mongo import Logging_Mongo
from library.utils.time_conv import timestamp2datetime

from .forms import Form_Login


class Base():
    def __init__(self, mongoclient=None, redisclient=None, log_mongoclient=None):
        self.logger = logging.getLogger("default")
        if mongoclient is None :
            self.mongoclient = Op_Mongo()
            self.logger.warn('无法继承，需要初始化mongodb连接')
        else :
            self.mongoclient = mongoclient
            
        if log_mongoclient is None :
            log_mongoclient = Op_Mongo(dest='log', idletime=30 * 24 * 60 * 60)
        self.log_mongoclient = log_mongoclient
        self.log2mongo_api = Logging_Mongo(mongoclient=log_mongoclient)
            
        if redisclient is None :
            self.redisclient = Op_Redis()
            self.logger.warn('无法继承，需要初始化redis连接')
        else :
            self.redisclient = redisclient

        self.usermanager_api = Manager_User(mongoclient=self.mongoclient, redisclient=self.redisclient)
        self.uri_api = Manager_Uri(mongoclient=self.mongoclient, redisclient=self.redisclient)
        # 由于mongodb的线程池没有完全掌握，在每隔class上直接初始化的话，导致连接数过多，使用过pickle等序列化写入redis，但没有解决掉
        # 上面是治标的方法，在urls时直接初始化，并携带给调用class上。
        # 在urls上直接初始化，这也有问题，可能导致过多用户数或者访问时，连接数不够用
        
        
    def _is_login(self, request):
        
        '''
        检查之前是否登录，username为session的用户
        '''
        
        try :
            self.username = request.session['username']
            if not self.username or not self.username:
                return (False, '该用户还没有登录')
            request.session['username'] = self.username
            # 每次访问页面，更新回话，用于防止登陆后，不管是否操作多保持规定时间
            http_host = request.META.get('HTTP_HOST')
            http_referer = request.META.get('HTTP_REFERER')
            self.whereabouts = self.uri_api.get_whereabouts(self.username, http_referer, http_host)
            self.nowtime = timestamp2datetime(fmt='%Y年%m月%d日 %H:%M:%S')
            
            try :
                self.nav_html = self.uri_api.get_nav(self.username)
            except :
                self.nav_html = ''
                
            self.latelywhere_html = self.uri_api.get_lately_whereabouts(self.username)
                
            return True
        except:
        # except Exception as e:
        #    print(e)
            return False


class Login(Base):
    def login(self, request):
        # 用户登录页面
        
        result = self.usermanager_api.get_userinfo(username=adminuser)
        if not result :
            self.logger.error('超级管理员' + adminuser + '不存在，正在创建中...')
            return HttpResponseRedirect(reverse('create_admin'))
        
        if request.method == 'GET' :
            result = self._is_login(request)
            if result:
                return HttpResponseRedirect(reverse('index'))
            else :
                form = Form_Login()
                return render(request, 'login.html', {'form': form})
        else:
            form = Form_Login(request.POST)
            if form.is_valid():
                username = request.POST.get('username')
                password = request.POST.get('password')
                
                result = self.usermanager_api.login(username, password)
                if not result[0] :
                    self.logger.error('用户' + username + '登陆失败，原因：' + result[1])
                    return render(request, 'login.html', {'form': form, 'error_message':result[1]})
                else :
                    self.log2mongo_api.write(username, '登陆', '登陆成功', level='info')
                    request.session['username'] = username
                    return HttpResponseRedirect(request.session.get('pre_url', reverse('index')))
            
                
    def create_admin(self, request):
        if request.method == 'GET' :
            result = self.usermanager_api.is_has(adminuser)
            if result :
                return HttpResponseRedirect(reverse('login'))
            else :
                return render(request, 'user_create_admin.html')
        else :
            form = Form_Login(request.POST)
            if form.is_valid():
                post_key_list = ['name', 'contact', 'password', 'password-confirm', 'ifpwd'] 
                user_mess_dict = {}
                for key in post_key_list :
                    user_mess_dict[key] = request.POST.get(key)
                    
                user_mess_dict['username'] = adminuser
                user_mess_dict['creater'] = adminuser
                
                result = self.usermanager_api.create(user_mess_dict)
                if not result[0] :
                    self.logger.error('超级管理员' + adminuser + '创建失败，原因：' + result[1])
                    return render(request, 'user_create_admin.html', {'error_message' : result[1]})
                else :
                    self.log2mongo_api.write(adminuser, '用户管理', '超级管理员创建成功', level='info')
                    return HttpResponseRedirect(reverse('index')) 
                
    
    def logout(self,request):
        username = request.session['username']
        self.log2mongo_api.write(username, '登出', '退出登录成功', level='info')
        from django.contrib import auth
        auth.logout(request)
        return HttpResponseRedirect(reverse('login'))

