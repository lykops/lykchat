from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls.base import reverse

from library.utils.time_conv import timestamp2datetime
from lykchat.forms import Form_Login
from lykchat.views import Base


class User(Base):
    def add(self, request):
        
        '''
        新增用户
        '''
        
        result = self._is_login(request)
        if not result :
            return HttpResponseRedirect(reverse('login'))
        
        if request.method == 'GET' :
            form = Form_Login()
            return render(request, 'user_add.html', {'form': form, 'login_user':self.username, 'nav_html':self.nav_html, 'lately_whereabouts':self.latelywhere_html})
        else:
            form = Form_Login(request.POST)
            if form.is_valid():
                post_key_list = ['username', 'name', 'contact', 'password', 'password-confirm', 'ifpwd'] 
                user_mess_dict = {}
                for key in post_key_list :
                    user_mess_dict[key] = request.POST.get(key)
                
                user_mess_dict['creater'] = self.username
                result = self.usermanager_api.create(user_mess_dict)
                if not result[0] :
                    error_message = '新增用户' + user_mess_dict['username'] + '失败，原因：' + result[1]
                    self.logger.error(error_message)
                    self.log2mongo_api.write(self.username, '用户管理', error_message, level='error')
                    http_referer = self.uri_api.get_httpreferer(self.username, no=-2)
                    return render(request, 'result.html', {'nowtime':self.nowtime, 'error_message' : error_message, 'http_referer':http_referer, 'nav_html':self.nav_html, 'lately_whereabouts':self.latelywhere_html})
                else :
                    self.log2mongo_api.write(self.username, '用户管理', ' 新增用户' + user_mess_dict['username'] + '成功', level='info')
                    return HttpResponseRedirect(reverse('user_list')) 
            

    def edit(self, request):
        
        '''
        编辑用户
        '''
        
        result = self._is_login(request)
        if not result :
            return HttpResponseRedirect(reverse('login'))
        
        username = request.GET.get('username')
        http_referer = self.uri_api.get_httpreferer(username, no=-2)
        result = self.usermanager_api.detail(username)
        if result[0]:
            data_dict = result[1]
            if not data_dict :
                error_message = '编辑用户' + username + '的基础信息失败，原因：用户不存在'
                self.log2mongo_api.write(self.username, '用户管理', error_message, level='error')
                return render(request, 'result.html', {'nowtime':self.nowtime, 'error_message' : error_message, 'http_referer':http_referer, 'nav_html':self.nav_html, 'lately_whereabouts':self.latelywhere_html})
        else :
            error_message = '编辑用户' + username + '的基础信息失败，查询用户信息时发生错误，原因：' + result[1]
            self.log2mongo_api.write(self.username, '用户管理', error_message, level='error')
            return render(request, 'result.html', {'nowtime':self.nowtime, 'error_message' : error_message, 'http_referer':http_referer, 'nav_html':self.nav_html, 'lately_whereabouts':self.latelywhere_html})

        if request.method == 'GET' :
            return render(request, 'user_edit.html', {'nowtime':self.nowtime, 'data_dict': data_dict, 'username':username, 'login_user':self.username, 'nav_html':self.nav_html, 'lately_whereabouts':self.latelywhere_html})
        else:
            form = Form_Login(request.POST)
            if form.is_valid():
                post_key_list = ['name', 'contact', 'ifpwd'] 
                user_mess_dict = {}
                for key in post_key_list :
                    user_mess_dict[key] = request.POST.get(key)
                
                user_mess_dict['username'] = request.GET.get('username')
                user_mess_dict['lastediter'] = self.username
                    
                result = self.usermanager_api.edit(user_mess_dict)
                if not result[0] :
                    error_message = '编辑用户' + username + '的基础信息失败，提交时发生错误，原因：' + result[1]
                    self.log2mongo_api.write(self.username, '用户管理', error_message, level='error')
                    http_referer = self.uri_api.get_httpreferer(username, no=-1)
                    return render(request, 'result.html', {'nowtime':self.nowtime, 'error_message' : error_message, 'http_referer':http_referer, 'nav_html':self.nav_html, 'lately_whereabouts':self.latelywhere_html})
                else :
                    self.log2mongo_api.write(self.username, '用户管理', '编辑用户' + user_mess_dict['username'] + '的基础信息成功', level='info')
                    return HttpResponseRedirect('/user/detail?username=' + username)
                
        
    def change_pwd(self, request):
        
        '''
        修改用户登陆密码
        '''
        
        result = self._is_login(request)
        if not result :
            return HttpResponseRedirect(reverse('login'))
        
        username = request.GET.get('username')
        if request.method == 'GET' :
            form = Form_Login()
            return render(request, 'user_chgpwd.html', {'nowtime':self.nowtime, 'form': form, 'username':username, 'login_user':self.username, 'nav_html':self.nav_html, 'lately_whereabouts':self.latelywhere_html})
        else:
            form = Form_Login(request.POST)
            if form.is_valid():
                user_mess_dict = {}
                user_mess_dict['username'] = request.GET.get('username')
                user_mess_dict['password'] = request.POST.get('password')
                user_mess_dict['password-confirm'] = request.POST.get('password-confirm')
                user_mess_dict['lastediter'] = self.username
                    
                result = self.usermanager_api.change_pwd(user_mess_dict)
                if not result[0] :
                    error_message = '编辑用户' + username + '的密码失败，提交时发生错误，原因：' + result[1]
                    self.log2mongo_api.write(self.username, '用户管理', error_message, level='error')
                    http_referer = self.uri_api.get_httpreferer(username, no=-1)
                    return render(request, 'result.html', {'nowtime':self.nowtime, 'error_message' : error_message, 'http_referer':http_referer, 'nav_html':self.nav_html, 'lately_whereabouts':self.latelywhere_html})
                else :
                    self.log2mongo_api.write(self.username, '用户管理', ' 编辑用户' + user_mess_dict['username'] + '的密码成功', level='info')
                    if self.username == user_mess_dict['username'] :
                        return HttpResponseRedirect(reverse('login'))
                    else :
                        return HttpResponseRedirect(reverse('user_list'))

                 
    def summary(self, request):
        
        '''
        用户列表
        '''
        
        result = self._is_login(request)
        if not result :
            return HttpResponseRedirect(reverse('login'))

        result = self.usermanager_api.summary()
        list_title_list = ['用户', '真实名', '是否激活' , '上次登录时间']
        if result[0] :
            self.logger.info(self.username + ' 获取所有用户信息时成功')
            return render(request, 'user_list.html', {'nowtime':self.nowtime, 'list_title_list':list_title_list, 'query_list':result[1], 'login_user':self.username, 'nav_html':self.nav_html, 'lately_whereabouts':self.latelywhere_html})
        else :
            error_message = self.username + ' 获取所有用户信息时失败，原因：' + result[1]
            self.logger.error(error_message)
            return HttpResponseRedirect(reverse('index'))
        

    def detail(self, request):
        
        '''
        查看用户详细信息
        '''
        
        result = self._is_login(request)
        if not result :
            return HttpResponseRedirect(reverse('login'))
            
        username = request.GET['username']
        result = self.usermanager_api.detail(username)
        if result[0] :
            self.logger.info(self.username + ' 查看用户' + username + '的详细数据成功')
            return render(request, 'user_detail.html', {'nowtime':self.nowtime, 'username':username, 'detail_dict':result[1] , 'login_user':self.username, 'nav_html':self.nav_html, 'lately_whereabouts':self.latelywhere_html})
        else :
            error_message = self.username + ' 查看用户' + username + '的详细数据，查询失败，原因：' + result[1]
            self.logger.error(error_message)
            return HttpResponseRedirect(reverse('index'))
  

    def disable(self, request):
        
        '''
        禁用用户登陆
        '''
        
        result = self._is_login(request)
        if not result :
            return HttpResponseRedirect(reverse('login'))
        
        username = request.GET.get('username')    
        result = self.usermanager_api.disable(username , editer=self.username)
        if not result[0] :
            error_message = '禁用用户' + username + '失败，原因：' + result[1]
            self.logger.error(error_message)
            self.log2mongo_api.write(self.username, '用户管理', error_message, level='error')
            http_referer = self.uri_api.get_httpreferer(username, no=-1)
            return render(request, 'result.html', {'nowtime':self.nowtime, 'error_message' : error_message, 'http_referer':http_referer, 'nav_html':self.nav_html, 'lately_whereabouts':self.latelywhere_html})
        else :
            self.logger.info('禁用用户' + username + '成功')
            self.log2mongo_api.write(self.username, '用户管理', '禁用用户' + username + '成功', level='info')
            return HttpResponseRedirect(reverse('user_list'))
             
                          
    def enable(self, request):
        
        '''
        允许用户登陆
        '''
        
        result = self._is_login(request)
        if not result :
            return HttpResponseRedirect(reverse('login'))
        
        username = request.GET.get('username')
        result = self.usermanager_api.enable(username , editer=self.username)
        if not result[0] :
            error_message = '启用用户' + username + '失败，原因：' + result[1]
            self.log2mongo_api.write(self.username, '用户管理', error_message, level='error')
            http_referer = self.uri_api.get_httpreferer(username, no=-1)
            return render(request, 'result.html', {'nowtime':self.nowtime, 'error_message' : error_message, 'http_referer':http_referer, 'nav_html':self.nav_html, 'lately_whereabouts':self.latelywhere_html})
        else :
            self.log2mongo_api.write(self.username, '用户管理', ' 启用用户' + username + '成功', level='info')
            return HttpResponseRedirect(reverse('user_list'))


    def get_logging(self, request):
        
        '''
        新增用户
        '''
        
        result = self._is_login(request)
        if not result :
            return HttpResponseRedirect(reverse('login'))
        
        result = self.log2mongo_api.read(self.username, limit=100)
        if not result[0] :
            log_list = []
        else :
            log_list = result[1]
        
        new_list = []
        for log_dict in log_list :
            datetime = timestamp2datetime(stamp=log_dict['add_time'])
            temp = [datetime, log_dict['modeule'], log_dict['level'], log_dict['content']]
            new_list.append(temp)
        
        new_list.reverse()
        http_referer = self.uri_api.get_httpreferer(self.username, no=-1)
        return render(request, 'logging.html', {'nowtime':self.nowtime, 'login_user':self.username, 'username' : self.username, 'log_list':new_list, 'http_referer':http_referer, 'nav_html':self.nav_html, 'lately_whereabouts':self.latelywhere_html})
        
