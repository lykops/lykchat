import json , os, django

from library.config.wechat import url_frond
from library.config.wechat import user_mess_dict
from library.keepalive.wechat.logininfo import Manage_Logininfo
from library.visit_url.request.cookie import Request_Url


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lykchat.settings")
django.setup()

def check_login() :
    op_info = Manage_Logininfo()
    all_session_dict = op_info.get_history_all()
    
    for username in all_session_dict :
        password = user_mess_dict[username]['interface_pwd']
        data = {
                'username':username,
                'password':password
            }
        
        data = json.dumps(data)
        url = url_frond + 'check_login?username=' + username + '&pwd=' + password
        
        open_url = Request_Url(url)
        url_req = open_url.return_context()
        print(url_req.text)
