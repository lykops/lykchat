import json, re, time, mimetypes, os
import random

from requests_toolbelt.multipart.encoder import MultipartEncoder

from library.config import wechat 
from library.file.get_md5 import get_file_md5
from library.visit_url.request.cookie import Request_Url

from .friend import Get_Friend 


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

        if msgType != 'txt' and (filename != '' and filename) :
            result_dict = self._upload_media(filename, tousername, msgType, content)
            return result_dict
        
        result_dict = self._send_text(tousername, content)
        return result_dict
        

    def _upload_media(self, filename, tousername, msgType, content):
        base_url = self.session_info_dict['login_info']['file_url']
        url = base_url + '/webwxuploadmedia?f=json'
        
        name = os.path.basename(filename)  # 文件名
        mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'  # MIME格式，注意是根据文件后缀名来确认的
        media_type = re.split(r'/' , mime_type)[0] or 'application'
        
        # 微信识别的文档格式
        if media_type == 'image' :
            media_type = 'pic'
        elif media_type == 'audio' or media_type == 'video' :
            media_type = 'video'
        else :
            media_type = 'doc' 
           
        # 当用户上传类型设置为file时，强制media_type设置为file 
        # if msgType == 'file' :
        #    media_type = 'doc'
        
        modts = os.path.getmtime(filename)  # 文件修改日期
        modstr = time.localtime(modts)
        lastModifieDate = time.strftime('%a %b %d %Y %H:%M:%S GMT+0800 (CST)', modstr)
        file_content = open(filename, 'rb')  
        file_size = os.path.getsize(filename)  # 文件大小
        chunksize = 524288  # 每个分开大小
        chunks = int((file_size - 1) / chunksize) + 1
        webwx_data_ticket = self.web_request_base_dict['cookies']['webwx_data_ticket']

        uploadmediarequest = json.dumps({
            'UploadType':2,
            "BaseRequest": self.base_request,
            "ClientMediaId": int(time.time() * 1000),
            "TotalLen": file_size,
            "StartPos": 0,
            "DataLen": file_size,
            "MediaType": 4,
            'FromUserName':self.myself['UserName'],
            'ToUserName':tousername,
            'FileMd5':get_file_md5(filename),
        }, ensure_ascii=False).encode('utf8')

        for chunk in range(chunks):
            ff = file_content.read(chunksize)
            if chunks == 1:
                multipart_encoder = MultipartEncoder(
                    fields={
                        'id': 'WU_FILE_0',
                        'name': name,
                        'type': mime_type,
                        'lastModifiedDate': lastModifieDate,
                        'size':str(file_size),
                        'mediatype': media_type,
                        'uploadmediarequest': uploadmediarequest,
                        'webwx_data_ticket': webwx_data_ticket,
                        'pass_ticket':self.pass_ticket,
                        'filename': (name , ff, mime_type)
                    },
                    boundary='---------------------------' + str(random.randint(1e28, 1e29 - 1))
                )
            else:
                multipart_encoder = MultipartEncoder(
                    fields={
                        'id': 'WU_FILE_0',
                        'name': name,
                        'type': mime_type,
                        'lastModifiedDate': lastModifieDate,
                        'size':str(file_size),
                        'chunks': str(chunks),
                        'chunk': str(chunk),
                        'mediatype': media_type,
                        'uploadmediarequest': uploadmediarequest,
                        'webwx_data_ticket': webwx_data_ticket,
                        'pass_ticket':self.pass_ticket,
                        'filename': (name , ff, mime_type)
                    },
                    boundary='---------------------------' + str(random.randint(1e28, 1e29 - 1))
                )

            self.web_request_base_dict['headers']['Origin-Type'] = 'https://wx2.qq.com'
            self.web_request_base_dict['headers']['Content-Type'] = multipart_encoder.content_type
    
            open_url = Request_Url(url, files=multipart_encoder, **self.web_request_base_dict)
            self.web_request_base_dict = open_url.return_web_request_base_dict()
            url_req = open_url.return_context()
            web_reselt_dict = json.loads(url_req.text)
        
        if web_reselt_dict['BaseResponse']['Ret'] != 0 :
            result_dict = {'Msg': '发送失败，上传文件失败', 'Code':-1008, 'ErrMsg': web_reselt_dict['BaseResponse']}
        else :
            mediaid = web_reselt_dict['MediaId']
            if mediaid :
                try :
                    if media_type == 'pic' :
                        result_dict = self._send_img(mediaid, tousername, content)
                    elif media_type == 'video':
                        result_dict = self._send_video(mediaid, tousername, content)
                    else :                
                        result_dict = self._send_file(mediaid, name, file_size, tousername, content)
                except :
                    result_dict = {'Msg': '发送失败，发送时出错', 'Code':-1009, 'ErrMsg': {}}
        
        if result_dict['Code'] != 0 :
            content = content + '\n文件发送失败，原因：\n' + str(result_dict)
    
        result_dict = self._send_text(tousername, content)
        return result_dict
        
 
    def _send_img(self, mediaid, tousername, content):
        '''
        发送图片
        '''
        base_url = self.login_info['url']
        url = base_url + '/webwxsendmsgimg?fun=async&f=json&lang=zh_CN'
        data = {
            'BaseRequest':self.base_request,
            'Msg':{
                'Type':3,
                'MediaId' :mediaid,
                'Content':content,
                "FromUserName":self.myself['UserName'],
                "ToUserName":tousername,
                "LocalID":self.msgid,
                "ClientMsgId":self.msgid
                },
            "Scene":0
            }
        data = json.dumps(data, ensure_ascii=False).encode('utf8')
        open_url = Request_Url(url, data=data , **self.web_request_base_dict)
        self.web_request_base_dict = open_url.return_web_request_base_dict()
        url_req = open_url.return_context()
        result_dict = self._handle_result(url_req)        
        return result_dict
    

    def _send_file(self, mediaid, name, file_size, tousername, content):
        '''
        发送普通文件
        '''
        base_url = self.login_info['url']
        url = base_url + '/webwxsendappmsg?fun=async&f=json&pass_ticket=' + self.pass_ticket
        fileend = re.split(r'.', name)[-1]  # 后缀名
        data = {
            'BaseRequest': self.base_request,
            'Msg': {
                'Type': 6,
                'Content': "<appmsg appid='wxeb7ec651dd0aefa9' sdkver=''><title>" + name + "</title><des></des><action></action><type>6</type><content>" + content + "</content><url></url><lowurl></lowurl><appattach><totallen>" + str(file_size) + "</totallen><attachid>" + mediaid + "</attachid><fileext>" + fileend + "</fileext></appattach><extinfo></extinfo></appmsg>",
                'FromUserName': self.myself['UserName'],
                'ToUserName': tousername,
                'LocalID': self.msgid,
                'ClientMsgId': self.msgid,
                },
            'Scene': 0,
            }
        data = json.dumps(data, ensure_ascii=False).encode('utf8')
        open_url = Request_Url(url, data=data , **self.web_request_base_dict)
        self.web_request_base_dict = open_url.return_web_request_base_dict()
        url_req = open_url.return_context()
        result_dict = self._handle_result(url_req)   
        return result_dict


    def _send_video(self, mediaid, tousername, content):
        '''
        发送视频文件
        '''
        base_url = self.login_info['url']
        url = base_url + '/webwxsendvideomsg?fun=async&f=json&lang=zh_CN'
        data = {
            'BaseRequest':self.base_request,
            'Msg':{
                'Type':43,
                'MediaId' :mediaid,
                'Content':content,
                "FromUserName":self.myself['UserName'],
                "ToUserName":tousername,
                "LocalID":self.msgid,
                "ClientMsgId":self.msgid
                },
            "Scene":0
            }
        self.login_info['msgid'] += 1
        data = json.dumps(data, ensure_ascii=False).encode('utf8')
        open_url = Request_Url(url, data=data , **self.web_request_base_dict)
        self.web_request_base_dict = open_url.return_web_request_base_dict()
        url_req = open_url.return_context()
        result_dict = self._handle_result(url_req)          
        return result_dict

        
    def _send_text(self, tousername, content):
        '''
        发送文字
        '''
        base_url = self.login_info['url']
        url = '%s/webwxsendmsg' % base_url
        data = {
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
        data = json.dumps(data, ensure_ascii=False).encode('utf8')
        open_url = Request_Url(url, data=data , **self.web_request_base_dict)
        self.web_request_base_dict = open_url.return_web_request_base_dict()
        url_req = open_url.return_context()
        result_dict = self._handle_result(url_req)          
        return result_dict


    def _handle_result(self, send_result):
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
        result_code = base_response.get('Ret' , -1006)

        try :
            err_msg = translation_dict[language][result_code]
        except :
            err_msg = '未知错误</br>'
      
        translation_value_dict = {'Msg' : err_msg , 'Code' : result_code, 'ErrMsg' :value_dict}
  
        if result_code == 1101 :
            translation_value_dict['ResCode'] = -1
            
        return translation_value_dict
