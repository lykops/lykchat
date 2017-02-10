import requests, re

from library.config import website


class Request_Url():
    # 使用requests模块访问web页面，必须提供url
    def __init__(self, url , session=False , headers={} , cookies={} , data={} , params={} , allow_redirects=True):
        if session == False :
            session = requests.Session()
        # 保持回话
        
        if headers == {} :
            headers = website.headers
        else :
            for header in ['Accept' ,'Accept-Encoding' ,'Accept-Language','Connection', 'Agent']:
                if header not in headers or headers[header] == '':
                    headers[header] = website.headers[header]
            # 新增headers

        url_protocol_list = ['http' , 'https']
        url_protocol = re.split('://' , url)[0]
        if not url_protocol in url_protocol_list :
            self.url = 'http://' + url
        else :
            self.url = url

        try :
            if data != {} :
                url_req = session.post(self.url, headers=headers , data=data, cookies=cookies , allow_redirects=allow_redirects)
                # print('post')
                # post方法
            else :
                url_req = session.post(self.url, headers=headers, cookies=cookies , allow_redirects=allow_redirects, params=params)
                # print('get')
                # get方法
        except Exception as e :
            print(e)
        
        # 访问后设置headers，用于后续访问，如果没有的，不设置
        try :
            for header in ['Content-Type' , 'Connection' , 'Domain', 'Referer']:
                if header in self.url_req.headers:
                    headers[header] = self.url_req.headers[header]
                
            if 'Content-Length' in self.url_req.headers :
                site_size = self.url_req.headers['Content-Length']
                self.site_size = int(site_size)
        except Exception as e :
            pass
            # print(e)

        self.headers = headers
        self.url_req = url_req
        self.cookies = dict(self.url_req.cookies)
        # 指定cookie，用于后续访问，微信中需要保持session即可
        self.session = session


    def return_web_request_base_dict(self):
        return {'session' : self.session , 'headers':self.headers , 'cookies':self.cookies}


    def return_context(self):
        return self.url_req
