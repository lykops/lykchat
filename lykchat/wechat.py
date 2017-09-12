import json

from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls.base import reverse

from library.frontend.wechat.interface import Manager_Interface
from library.frontend.wechat.single import Manager_Single
from lykchat.views import Base


class Wechat(Base):
    def __init__(self, mongoclient=None, redisclient=None, log_mongoclient=None):
        self.modname = '微信管理'
        super(Wechat, self).__init__(mongoclient=mongoclient, redisclient=redisclient, log_mongoclient=log_mongoclient)
    
    
    def summary(self, request):
        result = self._is_login(request)
        if not result :
            return HttpResponseRedirect(reverse('login'))

        force = request.GET.get('force', True)
        interface_api = Manager_Interface(self.username, redisclient=self.redisclient)
        result = interface_api.get_abs(force=force)
        if result[0] :
            msg = '获取所有微信号登陆信息时成功'
            self.logger.info(self.username + ' ' + msg)
            self.log2mongo_api.write(self.username, self.modname, msg, level='info')
            return render(request, 'list.html', {'nowtime':self.nowtime, 'abs_list':result[1], 'login_user':self.username, 'nav_html':self.nav_html, 'lately_whereabouts':self.latelywhere_html})
        else :
            msg = '获取所有用户信息时失败，原因：' + result[1]
            self.log2mongo_api.write(self.username, self.modname, msg, level='error')
            self.logger.error(self.username + ' ' + msg)
            return HttpResponseRedirect(reverse('index'))
        

    def detail(self, request):
        result = self._is_login(request)
        if not result :
            return HttpResponseRedirect(reverse('login'))
        
        uuid = request.GET.get('uuid', None)
        
        if request.method == 'GET' : 
            single_api = Manager_Single(self.username, uuid=uuid, redisclient=self.redisclient)
            result = single_api.index()
            if result[0] :
                login_user = result[1]
                status = login_user.get('status', 100)
                try :
                    wxnick = login_user.get('nickname', '')
                except :
                    wxnick = ''
                
                msg = '获取微信号【' + wxnick + '】登陆信息成功，登陆状态为' + str(status)
                self.logger.info(self.username + ' ' + msg)
                self.log2mongo_api.write(self.username, self.modname, msg, level='info')
                if uuid is None and status == 222 :
                    return HttpResponseRedirect('/wechat/detail?uuid=' + login_user.get('uuid', ''))
                else :
                    return render(request, 'detail.html', {'nowtime':self.nowtime, 'info_dict':login_user, 'login_user':self.username, 'nav_html':self.nav_html, 'lately_whereabouts':self.latelywhere_html})
            else :
                msg = '获取微信号【' + wxnick + '】登陆信息失败，原因：' + result[1]
                self.log2mongo_api.write(self.username, self.modname, msg, level='error')
                self.logger.error(self.username + ' ' + msg)
                return HttpResponseRedirect(reverse('wechat_list'))
        else :
            tousername = request.POST.get('username', '')
            content = request.POST.get('content', '')
            
            try :
                filename = request.FILES['file']
            except :
                filename = False
            
            single_api = Manager_Single(self.username, uuid=uuid, redisclient=self.redisclient)
            result = single_api.send_msg(tousername, content, filename=filename)
            
            self.log2mongo_api.write(self.username, self.modname, result[1]['send_result'], level='info')
            
            return render(request, 'detail.html', {'nowtime':self.nowtime, 'info_dict':result[1], 'login_user':self.username, 'nav_html':self.nav_html, 'lately_whereabouts':self.latelywhere_html})


    def logout(self, request):
        result = self._is_login(request)
        if not result :
            return HttpResponseRedirect(reverse('login'))

        uuid = request.GET.get('uuid', None)
        if uuid is None :
            err_msg = '请提供uuid'
            suc_msg = False
            self.log2mongo_api.write(self.username, self.modname, err_msg, level='error')
            self.logger.error(err_msg)
        else :
            single_api = Manager_Single(self.username, uuid=uuid, redisclient=self.redisclient)
            result = single_api.logout()
            if result[0] :
                suc_msg = '微信号' + result[1]['uuid'] + '退出成功'
                err_msg = False
                self.log2mongo_api.write(self.username, self.modname, suc_msg, level='info')
                self.logger.info(self.username + ' 微信' + result[1]['uuid'] + '退出成功')
            else :
                err_msg = '微信退出失败'  # ，原因：' + str(result[1])
                suc_msg = False
                self.log2mongo_api.write(self.username, self.modname, err_msg, level='error')
                try :
                    self.logger.error(self.username + ' 微信' + result[1]['uuid'] + '退出失败，原因：' + str(result[1]))
                except :
                    self.logger.error(self.username + ' 微信' + str(uuid) + '退出失败，原因：' + str(result[1]))
            
        interface_api = Manager_Interface(self.username, redisclient=self.redisclient)
        result = interface_api.get_abs(force=True)
        if result[0] :
            self.logger.info(self.username + ' 获取所有微信号登陆信息时成功')
            self.log2mongo_api.write(self.username, self.modname, '获取所有微信号登陆信息时成功', level='info')
            return render(request, 'list.html', {'nowtime':self.nowtime, 'abs_list':result[1], 'suc_msg':suc_msg, 'err_msg':err_msg, 'login_user':self.username, 'nav_html':self.nav_html, 'lately_whereabouts':self.latelywhere_html})
        else :
            err_msg = '获取所有用户信息时失败，原因：' + result[1]
            self.log2mongo_api.write(self.username, self.modname, err_msg, level='error')
            self.logger.error(self.username + ' ' + err_msg)
            return HttpResponseRedirect(reverse('index'))
        

    def check(self, request):
        ifpwd_def = 'adrqwerdafdsafw.hf456efsdcvadergfzv67cxfasrqwecxzvcxzgvdfsfa'
        uuid = request.GET.get('uuid', None)
        ifpwd = request.GET.get('ifpwd', ifpwd_def)
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ipaddr = x_forwarded_for.split(',')[-1].strip()
        else:
            ipaddr = request.META.get('REMOTE_ADDR')
        
        if uuid is None and ifpwd == ifpwd_def :
            self.username = '计划任务检测登陆用户'
            interface_api = Manager_Interface(self.username, redisclient=self.redisclient)
            result = interface_api.check_alluser(ipaddr)
            if result[1] :
                msg = self.username + '从【' + ipaddr + '】检测所有用户的微信号登陆情况成功'
                # self.log2mongo_api.write(self.username, self.modname, msg, level='info')
                self.logger.info(msg)
            else :
                msg = self.username + '从【' + ipaddr + '】检测所有用户的微信号登陆情况失败，原因：' + result[1]
                self.log2mongo_api.write(self.username, self.modname, msg, level='error')
                self.logger.error(msg)
        else :
            result = self._is_login(request)
            if not result :
                msg = '认证失败，原因：' + str(result[1])
                self.logger.info(msg)
                return HttpResponse(json.dumps((False, msg)), content_type="application/json")
            
            interface_api = Manager_Interface(self.username, redisclient=self.redisclient)
            result = interface_api.check_login(ifpwd, uuid)
            if uuid is None :
                if result[1] :
                    msg = self.username + '从【' + ipaddr + '】检测自己所有微信号登陆情况成功'
                    self.log2mongo_api.write(self.username, self.modname, msg, level='info')
                    self.logger.info(msg)
                else :
                    msg = self.username + '【从' + ipaddr + '】检测自己所有微信号登陆情况失败，原因：' + result[1]
                    self.log2mongo_api.write(self.username, self.modname, msg, level='error')
                    self.logger.error(msg)
            else :
                if result[1] :
                    msg = self.username + '从【' + ipaddr + '】检测微信号【' + uuid + '】登陆情况成功'
                    self.log2mongo_api.write(self.username, self.modname, msg, level='info')
                    self.logger.info(msg)
                else :
                    msg = self.username + '从【' + ipaddr + '】检测微信号【' + uuid + '】登陆情况失败，原因：' + result[1]
                    self.log2mongo_api.write(self.username, self.modname, msg, level='error')
                    self.logger.error(msg)

        return HttpResponse(json.dumps(result), content_type="application/json")

    
    def sendmsg(self, request):
        
        parameter_dict = {
            'username' : '用户' ,
            'pwd' : '接口密码，注意不等于登陆密码' ,
            'friend':'接受者的昵称，不能为空',
            'wxid':'发送者的昵称，能为空',
            'content':'发送内容，不能为空',
            'file':'发送的文件',
            'get方法测试url' : 'wechat/sendmsg?wxid=lyk-ops&username=zabbix&pwd=123456&friend=lyk-ops&content=test',
            '注意':'username、pwd、friend、content、wxid可以使用post和get传参，file必须post方式',
        }
        request_dict = {}
        for key in ['username', 'pwd', 'friend', 'content', 'wxid'] :
            try :
                try:
                    request_dict[key] = request.GET[key]
                except :
                    request_dict[key] = request.POST[key]
            except :
                request_dict[key] = ''
        
        ifpwd = request_dict.get('pwd', '')
        username = request_dict.get('username', '')
        tousername = request_dict.get('friend', '')
        content = request_dict.get('content', '')
        wxid = request_dict.get('wxid', None)
        
        try :
            filename = request.FILES['file']
        except :
            filename = False

        if not username :
            msg = '通过接口发送信息失败，原因：没有输入用户名'
            send_result = {'Code':-1101 , 'Msg' : msg, 'ErrMsg' : parameter_dict}
            self.log2mongo_api.write(username, self.modname, msg, level='error')
            self.logger.error(msg)
            return HttpResponse(json.dumps((False, send_result)), content_type="application/json")
        
        if not ifpwd :
            msg = username + '通过接口发送信息失败，原因：没有输入接口密码'
            send_result = {'Code':-1101 , 'Msg' : msg, 'ErrMsg' : parameter_dict}
            self.log2mongo_api.write(username, self.modname, msg, level='error')
            self.logger.error(msg)
            return HttpResponse(json.dumps((False, send_result)), content_type="application/json")
            
        if not tousername :
            msg = username + '通过接口发送信息失败，原因：没有输入接口密码'
            send_result = {'Code':-1101 , 'Msg' : msg, 'ErrMsg' : parameter_dict}
            self.log2mongo_api.write(username, self.modname, msg, level='error')
            self.logger.error(msg)
            return HttpResponse(json.dumps((False, send_result)), content_type="application/json")
            
        if not content :
            msg = username + '通过接口发送信息失败，原因：没有输入发送内容'
            send_result = {'Code':-1101 , 'Msg' : msg, 'ErrMsg' : parameter_dict}
            self.log2mongo_api.write(username, self.modname, msg, level='error')
            self.logger.error(msg)
            return HttpResponse(json.dumps((False, send_result)), content_type="application/json")
    
        interface_api = Manager_Interface(username, redisclient=self.redisclient)
        result = interface_api.sendmsg(ifpwd, tousername, content, filename=filename, wxid=wxid, post_field='NickName')
        if result[0] :
            msg = username + '通过接口发送信息成功'
            send_dict = result[1].get('ok', {})
            nickname = send_dict.get('nickname', '')
            friend = send_dict.get('friend', tousername)
            file_dict = send_dict.get('file', {})
            text_dict = send_dict.get('text', {})
            file_content = file_dict.get('msg', '')
            uploadfile = file_dict.get('filename', '')
            text_content = text_dict.get('msg', '')

            contents = '微信号【' + str(nickname) + '】调用接口</br>向【' + str(friend) + '】发送信息，结果如下：</br>'
            contents = contents + '文字【' + str(content) + '】' + text_content + '</br>'
            contents = contents + '文件【' + str(uploadfile) + '】' + file_content
            
            self.log2mongo_api.write(username, self.modname, contents, level='info')
        else :
            msg = '调用接口发送信息失败'
            # ，原因：' + str(result[1])
            self.log2mongo_api.write(username, self.modname, msg, level='error')
            self.logger.error(username + msg + ' ，原因：' + str(result[1]))
        return HttpResponse(json.dumps(result), content_type="application/json")
