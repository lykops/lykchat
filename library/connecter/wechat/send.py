import json, re, time, os
import mimetypes
from requests_toolbelt.multipart.encoder import MultipartEncoder

from library.connecter.visit_url.cookie import Request_Url
from library.connecter.wechat import Base
from library.utils.file import get_filetype
from library.utils.get_md5 import get_file_md5
from library.utils.type_conv import random_str

from .friend import Get_Friend 


class Send_Msg(Base):
    
    '''
    接受和发送信息
    '''

    def send(self, content, filename='', tousername='filehelper' , post_field='UserName'):
        
        '''
        发送信息，返回类型为字典
        '''
        
        get_friend = Get_Friend(self.session_info_dict)
        result = get_friend.get_singlefriend_dict(tousername, post_field=post_field)
        if result[0] :
            friend_dict = result[1]
        else :
            self.logger.error('找到好友时出错,' + result[1])
            return {'Msg': '找到好友时出错,' + result[1], 'Code':-1102, 'ErrMsg':'找到好友时出错', 'friend':''}

        tousername = friend_dict.get('UserName', '')
        self.nickname = friend_dict.get('NickName', '')

        if not re.search('@', tousername) and tousername != 'filehelper':
            self.logger.warn('找到好友时出错，没有找到指定好友')
            return {'Msg': '找到好友时出错，没有找到指定好友', 'Code':-1102, 'ErrMsg':'没有找到指定好友', 'friend':''}

        if filename :
            result = self._send_media(filename, tousername, content)
        else :
            result = self._send_text(tousername, content)
        
        return result


    def _send_media(self, filename, tousername, content):
        file_url = self.login_info['file_url']
        url = file_url + '/webwxuploadmedia?f=json'
        
        result = get_filetype(filename)
        self.logger.info(result)
        if result[0] :
            mime_type = result[2]
            media_type = re.split(r'/' , mime_type)[0] or 'application'
            name = 'lykchat.' + filename.split('.')[-1]
        else :
            mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'  # MIME格式，注意是根据文件后缀名来确认的
            media_type = re.split(r'/' , mime_type)[0] or 'application'
            name = 'lykchat'
        # 修改name是用来解决中文文件名的情况
        
        # 微信识别的文档格式
        if media_type == 'image' :
            media_type = 'pic'
        elif media_type == 'audio' or media_type == 'video' :
            media_type = 'video'
        else :
            media_type = 'doc' 

        # orig_name = os.path.basename(filename)  # 文件名
        modts = os.path.getmtime(filename)  # 文件修改日期
        modstr = time.localtime(modts)
        lastModifieDate = time.strftime('%a %b %d %Y %H:%M:%S GMT+0800 (CST)', modstr)
        file_content = open(filename, 'rb')  
        file_size = os.path.getsize(filename)  # 文件大小
        chunksize = 524288  # 每个分块大小
        chunks = int((file_size - 1) / chunksize) + 1
        webwx_data_ticket = self.web_request_base_dict['cookies']['webwx_data_ticket']

        if file_size == 0 :
            msg = '文件为0字节，无法上传到微信失败'
            return {'Msg': msg, 'Code':-1009, 'ErrMsg': msg, 'friend':self.nickname}

        uploadmediarequest_dict = {
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
        }

        uploadmediarequest = json.dumps(uploadmediarequest_dict, ensure_ascii=False).encode('utf8')

        for chunk in range(chunks):
            ff = file_content.read(chunksize)
            
            field_dict = {
                'id': 'WU_FILE_0',
                'name': name,
                'type': mime_type,
                'lastModifiedDate': lastModifieDate,
                'size':str(file_size),
                'chunks':str(chunks),
                'chunk':str(chunk),
                'mediatype': media_type,
                'uploadmediarequest': uploadmediarequest,
                'webwx_data_ticket': webwx_data_ticket,
                'pass_ticket':self.pass_ticket,
                'filename': (name , ff, mime_type)
                }
            boundarys = '------WebKitFormBoundary' + random_str(16)
            # boundarys='---------------------------' + str(random.randint(1e28, 1e29 - 1))
            multipart_encoder = MultipartEncoder(
                fields=field_dict,
                boundary=boundarys
                )
            self.web_request_base_dict['headers']['Origin-Type'] = self.base_url
            self.web_request_base_dict['headers']['Content-Type'] = multipart_encoder.content_type
    
            open_url = Request_Url(url, files=multipart_encoder, **self.web_request_base_dict)
            self.web_request_base_dict = open_url.return_web_request_base_dict()
            try :
                url_req = open_url.return_context()
                web_reselt_dict = json.loads(url_req.text)
                if web_reselt_dict['BaseResponse']['Ret'] != 0 :
                    msg = '文件上传到微信失败，被微信拒绝'
                    self.logger.warn(msg)
                    return {'Msg': msg, 'Code':2101, 'ErrMsg': web_reselt_dict, 'friend':self.nickname}
            except Exception as e :
                msg = '文件上传到微信失败，微信返回异常，' + str(e)
                self.logger.warn(msg)
                return {'Msg': msg, 'Code':2100, 'ErrMsg': e, 'friend':self.nickname}
                
        mediaid = web_reselt_dict['MediaId']
        if mediaid :
            self.msgid = int(time.time() * 1000 * 1000 * 10)
            try :
                if media_type == 'pic' :
                    result = self._send_img(mediaid, tousername, content)
                elif media_type == 'video':
                    result = self._send_video(mediaid, tousername, content)
                else :                
                    result = self._send_file(mediaid, name, file_size, tousername, content)
                        
                return result
            except Exception as e:
                msg = '文件发送失败，执行时代码出现异常，' + str(e)
                self.logger.error(msg)
                return {'Msg': msg, 'Code':-1009, 'ErrMsg': msg, 'friend':self.nickname}
        else :
            msg = '文件上传到微信失败，被微信拒绝'
            self.logger.warn(msg)
            return {'Msg':msg, 'Code':-1008, 'ErrMsg': web_reselt_dict, 'friend':self.nickname}
        
       
    def _send_img(self, mediaid, tousername, content):
        
        '''
        发送图片
        '''
        
        # url = self.mmwebwx_url + '/webwxsendmsgimg?fun=async&f=json&lang=zh_CN'
        url = self.mmwebwx_url + '/webwxsendmsgimg?fun=async&f=json&lang=en_US'
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
        result_dict = self._handle_result(open_url)        
        return result_dict
    

    def _send_file(self, mediaid, name, file_size, tousername, content):
        
        '''
        发送普通文件
        '''
        
        url = self.mmwebwx_url + '/webwxsendappmsg?fun=async&f=json&pass_ticket=' + self.pass_ticket
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
        result_dict = self._handle_result(open_url)   
        return result_dict


    def _send_video(self, mediaid, tousername, content):
        
        '''
        发送视频文件
        '''
        
        # url = self.mmwebwx_url + '/webwxsendvideomsg?fun=async&f=json&lang=zh_CN'
        url = self.mmwebwx_url + '/webwxsendvideomsg?fun=async&f=json&lang=en_US'
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
        result_dict = self._handle_result(open_url)          
        return result_dict

        
    def _send_text(self, tousername, content):
        
        '''
        发送文字
        '''
        
        url = '%s/webwxsendmsg' % self.mmwebwx_url
        self.msgid = int(time.time() * 1000 * 1000 * 10)
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
        data = json.dumps(data, ensure_ascii=False).encode('utf8')
        open_url = Request_Url(url, data=data , **self.web_request_base_dict)
        result_dict = self._handle_result(open_url)          
        return result_dict


    def _handle_result(self, open_url):
        
        '''
        返回发送信息结果，返回类型为字典
        '''
        
        try :
            self.web_request_base_dict = open_url.return_web_request_base_dict()
            send_result = open_url.return_context()
        except Exception as e :
            msg = '微信端返回异常'
            self.logger.error(msg)
            return {'Msg': msg + '，' + str(e), 'Code':2000, 'ErrMsg': msg + '，' + str(e), 'friend':self.nickname}
        
        value_dict = {}
        if send_result:
            try:
                value_dict = send_result.json()
                base_response = value_dict['BaseResponse']
            except Exception as e:
                msg = '微信端返回异常'
                self.logger.error(msg)
                return {'Msg': msg + '，' + str(e), 'Code':2000, 'ErrMsg': msg + '，' + str(e), 'friend':self.nickname}
        else :
            msg = '微信端返回异常'
            self.logger.error(msg)
            return {'Msg': msg + '，' + str(e), 'Code':2000, 'ErrMsg': msg + '，' + str(e), 'friend':self.nickname}

        result_code = base_response.get('Ret' , -1006)
        try :
            err_msg = self.sendresult_translation_dict[self.language][result_code]
        except :
            err_msg = '未知错误'
        translation_value_dict = {'Msg' : err_msg , 'Code' : result_code, 'ErrMsg' :value_dict, 'friend':self.nickname}
  
        if result_code == 1101 :
            translation_value_dict['ResCode'] = -1
            
        return translation_value_dict
