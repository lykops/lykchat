from collections import OrderedDict
import json, re, time, mimetypes, os

import requests

from library.config import wechat 
from library.file.get_md5 import get_file_md5
from library.visit_url.request.cookie import Request_Url

from .friend import Get_Friend 


# import requests
# from requests_toolbelt.multipart.encoder import MultipartEncoder
class Send_Msg():
    '''
    接受和发送信息
    '''
    def __init__(self, session_info_dict):
        self.session_info_dict = session_info_dict
        self.login_info = self.session_info_dict['login_info']
        self.web_request_base_dict = self.session_info_dict['web_request_base_dict']
        self.base_request = self.login_info['BaseRequest']
        self.myself = self.session_info_dict['myself']
        self.msgid = int(time.time() * 1000 * 1000 * 10)
        self.pass_ticket = self.login_info['pass_ticket']


    def send(self, content, msgType='txt', filename='', tousername='filehelper' , post_field='UserName'):
        '''
        发送信息，返回类型为字典
        '''
        get_friend = Get_Friend(self.session_info_dict)
        friend_dict = get_friend.get_singlefriend_dict(tousername, post_field=post_field)

        try :
            tousername = friend_dict['UserName']
        except :
            tousername = ''
        
        if not re.search('@', tousername) and tousername != 'filehelper':
            return {'Msg': '发送失败，账号设置错误', 'Code':-1102, 'ErrMsg':'无法找到好友'} 
        
        if msgType == 'txt' :
            result_dict = self._txtmsg(tousername, content)
            return result_dict
        if msgType != 'txt' and (filename != '' and filename) :
            result_dict = self._txtmsg(tousername, content)
            
            self._uploadmedia(filename, tousername, msgType)
            return result_dict
        
        
        result_dict = self._txtmsg(tousername, content)
        return result_dict
        

    def _uploadmedia(self, filename, tousername, msgType):
        base_url = self.session_info_dict['login_info']['file_url']
        url = base_url + '/webwxuploadmedia?f=json'
        
        # 文件名
        name = os.path.basename(filename)
        
        # MIME格式，注意是根据文件后缀名来确认的
        mime_type =  mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        
        # 微信识别的文档格式，微信服务器应该只支持两种类型的格式。pic和doc
        # pic格式，直接显示。doc格式则显示为文件。
        if msgType == 'img' :
            media_type = 'pic' 
        else : 
            media_type = 'doc'
        
        # 上一次修改日期
        modts = os.path.getmtime(filename)
        modstr = time.localtime(modts)
        lastModifieDate = time.strftime('%a %b %d %Y %H:%M:%S GMT+0800 (CST)', modstr)
        # 文件大小
        file_content = open(filename, 'rb')
        # .read()
        file_size = os.path.getsize(filename)
        chunksize = 524288
        chunks = int((file_size - 1) / chunksize) + 1
        webwx_data_ticket = self.web_request_base_dict['cookies']['webwx_data_ticket']
        
        uploadmediarequest = OrderedDict([
            ('UploadType', 2),
            ('BaseRequest', self.base_request),
            ('ClientMediaId', int(time.time() * 1000)),
            ('TotalLen', file_size),
            ('StartPos', 0),
            ('DataLen', file_size),
            ('MediaType', 4),
            ('FromUserName', self.myself['UserName']),
            ('ToUserName', tousername),
            ('FileMd5', get_file_md5(filename))]
        )
        uploadmediarequest = json.dumps(uploadmediarequest, separators=(',', ':'))
    
        for chunk in range(chunks):
            ff = file_content.read(chunksize)
            files = OrderedDict([
                ('id', 'WU_FILE_0'),
                ('name', name),
                ('type', mime_type),
                ('lastModifiedDate', lastModifieDate),
                ('size', str(file_size)),
                ('chunks', None),
                ('chunk', None),
                ('mediatype', media_type),
                ('uploadmediarequest', uploadmediarequest),
                ('webwx_data_ticket', webwx_data_ticket),
                ('pass_ticket', self.pass_ticket),
                # ('filename', (name, ff , 'application/octet-stream'))
                # ('filename', (name, ff , mime_type))
                ])
            
            if chunks == 1:
                del files['chunk']; del files['chunks']
            else:
                files['chunk'], files['chunks'] = str(chunk), str(chunks)
    
            self.web_request_base_dict['headers']['Origin-Type'] = 'https://wx2.qq.com'
            self.web_request_base_dict['headers']['Accept'] = '*/*'
            self.web_request_base_dict['headers']['Content-Type'] = 'multipart/form-data; boundary=---------------------------160092666810849'
    
            open_url = Request_Url(url, data=files , files={'filename':(name, ff , mime_type)} , **self.web_request_base_dict)
            self.web_request_base_dict = open_url.return_web_request_base_dict()
            url_req = open_url.return_context()
            web_reselt_dict = json.loads(url_req.text)
            print(web_reselt_dict)
            
            url_req = requests.options(url, headers=self.web_request_base_dict['headers'], cookies=self.web_request_base_dict['cookies'])
        
        if web_reselt_dict['BaseResponse']['Ret'] != 0 :
            return False
        
        return web_reselt_dict['MediaId']
 
        
    def _txtmsg(self, tousername, content):
        base_url = self.login_info['url']
        url = '%s/webwxsendmsg' % base_url
        payloads = {
            'BaseRequest': self.base_request,
            'Msg': {
                'Type': 'Test Message',
                'Content': content,
                'FromUserName': self.myself['UserName'],
                'ToUserName': tousername,
                'LocalID': self.msgid,
                'ClientMsgId': self.msgid,
                },
            'Scene' : 0
            }
        
        self.login_info['msgid'] += 1
        data = json.dumps(payloads, ensure_ascii=False).encode('utf8')
        open_url = Request_Url(url, data=data , **self.web_request_base_dict)
        self.web_request_base_dict = open_url.return_web_request_base_dict()
        url_req = open_url.return_context()
        
        result_dict = self._send_result(url_req)          
        return result_dict


    def _send_result(self, send_result):
        '''
        返回发送信息结果，返回类型为字典
        '''
        value_dict = {}
        language = wechat.language
        translation_dict = wechat.sendresult_translation_dict
        
        if send_result:
            try:
                value_dict = send_result.json()
            except ValueError:
                value_dict = {
                    'BaseResponse': {
                        'Ret': -1004,
                        'ErrMsg': 'Unexpected return value', },
                    'Data': '', }

        base_response = value_dict['BaseResponse']
        # raw_msg = base_response.get('ErrMsg', '')
        result_code = base_response.get('Ret' , -1006)

        try :
            err_msg = translation_dict[language][result_code]
        except :
            err_msg = '未知错误</br>'
      
        translation_value_dict = {'Msg' : err_msg , 'Code' : result_code, 'ErrMsg' :value_dict}
  
        if result_code == 1101 :
            translation_value_dict['ResCode'] = -1
            
        return translation_value_dict
