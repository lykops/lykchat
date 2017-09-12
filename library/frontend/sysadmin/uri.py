import re

from library.frontend import Base
from library.utils.type_conv import str2list


class Manager_Uri(Base):
    def __init__(self, mongoclient=None, redisclient=None):
        self.uridict = {
            '/':{'name':'首页', 'nav':False, 'referer' : True, 'level':0, 'parent':'/'},
            '/login.html':{'name':'登陆', 'nav':False, 'referer' : False, 'level':1, 'parent':'/'},
            '/logout.html':{'name':'退出', 'nav':False, 'referer' : False, 'level':1, 'parent':'/'},
            
            '/user/':{'name':'用户管理', 'nav':True, 'referer' : True, 'level':1, 'parent':'/'},
            '/user/create_admin':{'name':'创建管理员', 'nav':False, 'referer' : True, 'level':2, 'parent':'/user/'},
            '/user/detail':{'name':'用户信息', 'nav':False, 'referer' : True, 'level':2, 'parent':'/user/'},
            '/user/list':{'name':'用户列表', 'nav':False, 'referer' : True, 'level':2, 'parent':'user/'},
            '/user/add':{'name':'新增用户', 'nav':False, 'referer' : True, 'level':2, 'parent':'/user/'},
            '/user/edit':{'name':'编辑用户', 'nav':False, 'referer' : True, 'level':2, 'parent':'/user/'},
            '/user/chgpwd':{'name':'修改用户登陆密码', 'nav':False, 'referer' : True, 'level':2, 'parent':'/user/'},
            '/user/chgpvltwd':{'name':'修改用户机密密码 ', 'nav':False, 'referer' : True, 'level':2, 'parent':'/user/'},
            '/user/del':{'name':'删除用户', 'nav':False, 'referer' : False, 'level':2, 'parent':'/user/'},
            '/user/disable':{'name':'禁用用户', 'nav':False, 'referer' : False, 'level':2, 'parent':'/user/'},
            '/user/enable':{'name':'启用用户', 'nav':False, 'referer' : False, 'level':2, 'parent':'/user/'},
            
            '/wechat/':{'name':'微信管理', 'nav':True, 'referer' : True, 'level':1, 'parent':'/'},
            '/wechat/list':{'name':'微信列表', 'nav':False, 'referer' : True, 'level':2, 'parent':'wechat/'},
            '/wechat/detail':{'name':'微信登陆信息详情', 'nav':False, 'referer' : True, 'level':2, 'parent':'wechat/'},
            '/wechat/logout':{'name':'微信登出', 'nav':False, 'referer' : False, 'level':2, 'parent':'wechat/'},
            '/wechat/check':{'name':'微信登陆状态检查', 'nav':False, 'referer' : False, 'level':2, 'parent':'wechat/'},
            '/wechat/sendmsg':{'name':'微信发送信息', 'nav':False, 'referer' : False, 'level':2, 'parent':'wechat/'},
            
            
            '/logging/':{'name':'查看日志', 'nav':True, 'referer' : True, 'level':1, 'parent':'/'},
            }
        
        super(Manager_Uri, self).__init__(mongoclient=mongoclient, redisclient=redisclient)


    def get_nav(self, username, force=False):
        
        '''
        获取左侧栏信息
        '''
        
        redis_key = 'lykops:' + username + ':uri:nav'
        if force:
            self.logger.warn('强制删除缓存')
            self.redisclient.delete(redis_key)
        else :
            result = self.redisclient.get(redis_key)
            if not result[0] or (result[1] is None or not result[1]) :
                nav_str = result[1]
                return nav_str
            
        nav_str = self.gen_nav(username)
        set_dict = {
            'name' : redis_key,
            'value' : nav_str,
            'ex':self.expiretime
            }
        self.redisclient.set(set_dict, fmt='obj')
        return nav_str
    
    
    def gen_nav(self, username):
        
        '''
        生成左侧栏信息，注意：目前只支持两级
        '''
        
        nav_dict = {}
        for uri, value in self.uridict.items() :
            if value['nav'] :
                nav_dict[uri] = value

        uri_dict = {}
        for key, value in nav_dict.items() :
            level = value['level']
            if level == 1 :
                if key not in uri_dict :
                    uri_dict[key] = {}
                
                for childkey, childvalue in nav_dict.items() :
                    if childvalue['parent'] == key:
                        uri_dict[key][childkey] = {}
                          
        for key, value in nav_dict.items() :
            level = value['level']
            if level == 2 :
                parent = value['parent']
                if key not in uri_dict[parent] :
                    uri_dict[parent][key] = {}
                
                for childkey, childvalue in nav_dict.items() :
                    if childvalue['parent'] == key:
                        uri_dict[parent][key][childkey] = {}
        
        nav_str = ''
        
        for key,value in uri_dict.items() :
            if not value :
                name = self.uridict[key]['name']
                nav_str = nav_str + "<ul class='nav nav-first-level'>" + "\n"
                nav_str = nav_str + "<li class='" + name + "'><a href='" + key + "'>" + name + "</a></li>" + "\n"
            else :
                frist_title =  self.uridict[key]['name']
                nav_str = nav_str + "<ul class='nav nav-first-level'>" + "\n"
                nav_str = nav_str + "<li id='"+frist_title+"'>" + "\n"
                nav_str = nav_str + "<a href='#'><i class='fa fa-group'></i><span class='nav-label'>"+frist_title+"</span><span class='fa arrow'></span></a>" + "\n"
                for k in value :
                    name = self.uridict[k]['name']
                    nav_str = nav_str + "<ul class='nav nav-second-level'>" + "\n"
                    nav_str = nav_str + "<li class='" + name + "'><a href='" + k + "'>" + name + "</a></li>" + "\n"
                    nav_str = nav_str + "</ul>" + "\n"
                    
                nav_str = nav_str + "</li>\n</ul>\n"

        return nav_str
        

    def get_httpreferer(self, username, no=-1):
        
        '''
        返回http_referer
        '''
        
        redis_key = self.rediskey_prefix + username + ':whereabouts'
        result = self.redisclient.get(redis_key, fmt='obj')
        if result[0] :
            whereabouts = result[1]
        else :
            whereabouts = []
        
        try :
            http_referer = whereabouts[no]['http_referer']
        except :
            http_referer = '/'
        
        return http_referer
        
        
    def get_lately_whereabouts(self, username):
        
        '''
        获取最近的访问路劲
        '''
        
        redis_key = self.rediskey_prefix + username + ':whereabouts'
        result = self.redisclient.get(redis_key, fmt='obj')
        if result[0] :
            whereabouts = result[1]
        else :
            whereabouts = []
        
        try :
            lastly = whereabouts[-5:-1]
        except :
            lastly = []
        
        lastly_html = '<strong>最近的访问路径：'
        leng = len(lastly)
        for i in range(leng) :
            path = lastly[i]
            if i + 1 == leng :
                lastly_html = lastly_html + '<a href="' + path['http_referer'] + '">' + path['name'] + '</a>\n'
            else :
                lastly_html = lastly_html + '<a href="' + path['http_referer'] + '">' + path['name'] + '</a>==>\n'

        lastly_html = lastly_html + '</strong>'
        return lastly_html
    
        
    def get_whereabouts(self, username, http_referer, http_host):
        
        '''
        记录访问路径
        '''
        
        if http_referer is not None :
            path_info = http_referer.replace('http://' + http_host, '')
            path_info = path_info.replace('https://' + http_host, '')
            http_referer = path_info
            
            if re.search('\?', path_info) :
                end = re.split('\?', path_info)[-1]
                path_info = path_info.replace('?' + end, '')
        else :
            path_info = '/'
                  
        redis_key = self.rediskey_prefix + username + ':whereabouts'
        result = self.redisclient.get(redis_key, fmt='obj')
        if result[0] :
            whereabouts = result[1]
            result = str2list(whereabouts)
            if result[0] :
                whereabouts = result[1]
                if whereabouts[-1]['http_referer'] == http_referer or http_referer is None:
                    return whereabouts
            else :
                if http_referer is None:
                    return []
                else :
                    whereabouts = []
        else :
            whereabouts = []
        
        try :
            path_dict = self.uridict[path_info]
            if path_dict['referer'] :
                name = path_dict['name']
            else :
                return whereabouts
        except :
            print('请把' + path_info + '加入到self.uridict')
            self.logger.warn('请把' + path_info + '加入到self.uridict')
            return whereabouts
            
        try :
            self.redisclient.delete(redis_key)
        except :
            pass
            
        path_dict = {
            'name' : name ,
            'http_referer' : http_referer
            }
            
        if whereabouts :
            whereabouts.append(path_dict)
        else :
            whereabouts = [path_dict]

        set_dict = {
            'name' : redis_key,
            'value' : whereabouts,
            'ex':self.expiretime
            }
        self.redisclient.set(set_dict, fmt='obj')
        return whereabouts
