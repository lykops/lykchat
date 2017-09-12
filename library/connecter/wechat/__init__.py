import logging
import os, platform

import library.config.wechat as wechat_conf
from library.storage.cache import Manager_Cache
from library.storage.database.mongo import Op_Mongo
from library.storage.logging.mongo import Logging_Mongo

class Base():
    def __init__(self, session_info_dict={}):
        self.logger = logging.getLogger("wechat")
        self.curr_dir = wechat_conf.curr_dir
        self.qr_dir = wechat_conf.qr_dir
        self.appid = wechat_conf.appid
        self.login_status_code_dict = wechat_conf.login_status_code_dict
        self.language = wechat_conf.language
        self.sendresult_translation_dict = wechat_conf.sendresult_translation_dict
        self.max_upload_size = wechat_conf.max_upload_size
        self.base_dir = wechat_conf.BASE_DIR
        self.friendlist_field_list = wechat_conf.friendlist_field_list
        # 加载配置

        self.session_info_dict = session_info_dict
        self.web_request_base_dict = self.session_info_dict.get('web_request_base_dict', {})
        self.uuid = self.session_info_dict.get('uuid', None)
        self.status = self.session_info_dict.get('status', 100)
        self.redirect_uri = self.session_info_dict.get('redirect_uri', '')
        self.login_info = self.session_info_dict.get('login_info', {})
        self.friend_list = self.session_info_dict.get('friend_list', {})
        self.base_url = self.session_info_dict.get('url', wechat_conf.base_url)
        self.sid = self.session_info_dict.get('sid', '')
        self.uin = self.session_info_dict.get('uin', '')
        self.deviceid = self.session_info_dict.get('deviceid', '')
        self.synckey = self.session_info_dict.get('synckey', '')
        self.SyncKey = self.session_info_dict.get('SyncKey', '')
        self.sync_url = self.session_info_dict.get('sync_url', '')
        self.mmwebwx_url = self.login_info.get('url', self.base_dir)
        self.myself = self.session_info_dict.get('myself', {})
        self.base_request = self.login_info.get('BaseRequest', {})
        self.skey = self.login_info.get('skey', '')
        self.pass_ticket = self.login_info.get('pass_ticket', '')
        self.firstpage_contactlist = self.session_info_dict.get('firstpage_contactlist', [])
        self.groupuser_list = self.session_info_dict.get('groupuser_list', [])
                
        if not self.friend_list :
            for field in self.friendlist_field_list:
                self.friend_list[field] = []
