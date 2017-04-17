import requests, re

class Request_Url():
    '''
    使用requests模块访问web页面，必须提供url
    '''
    def __init__(self, url, headers={}, cookies={}, data={}, files={}, params={}, allow_redirects=True):
        default_headers = {
            'Accept' : 'application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding' : 'gzip, deflate, br',
            'charset': 'UTF-8',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.5,zh;q=0.3',
            'Connection': 'keep-alive',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0',
            }

        if headers == {} :
            headers = default_headers
        else :
            for header in ['Accept' , 'Accept-Encoding' , 'Accept-Language', 'Connection', 'User-Agent']:
                if header not in headers or headers[header] == '':
                    headers[header] = default_headers[header]
            # 新增headers

        url_protocol_list = ['http' , 'https']
        url_protocol = re.split('://' , url)[0]
        if not url_protocol in url_protocol_list :
            self.url = 'http://' + url
        else :
            self.url = url
            
        try :
            if data != {} :
                url_req = requests.post(self.url, headers=headers , data=data, cookies=cookies , allow_redirects=allow_redirects)
                # post方法
            elif files != {} :
                url_req = requests.post(self.url, data=files, headers=headers, timeout=300)
            else :
                url_req = requests.get(self.url, headers=headers, cookies=cookies , allow_redirects=allow_redirects, params=params)
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
        except :
            pass

        self.headers = headers
        self.url_req = url_req
        new_cookies = dict(self.url_req.cookies)

        if new_cookies != cookies  or new_cookies != {}:
            for k, v in new_cookies.items() :
                cookies[k] = v
        # 更新cookies
        
        self.cookies = cookies
        # 指定cookie，用于后续访问，微信中需要保持session即可


    def return_web_request_base_dict(self):
        return {'headers':self.headers , 'cookies':self.cookies}


    def return_context(self):
        return self.url_req
