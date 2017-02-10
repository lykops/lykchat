import threading , time
# os,django
#django.setup()
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lykchat.settings")


from library.wechat.friend import Get_Friend
from library.wechat.login import Login
from library.wechat.ready import Ready
from library.wechat.receive import Receive_Msg
from library.wechat.send import Send_Msg

status = -1
ready = Ready()
(uuid, web_request_base_dict) = ready.return_basicinfo_dict()
# web请求基础参数

while 1 :
    if status == 200 :
        break
    else :
        (status, redirect_uri) = ready.check_status()
        time.sleep(5)
# 以上操作仅仅登陆，不会获取微信号任何信息，在电脑端或者web页面登陆不会退出
# 但是下一步就不同了


login = Login(web_request_base_dict, redirect_uri=redirect_uri)
login_info = login.get_logininfo()


starttime = int(time.time())
print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
def receive_func(login_info, web_request_base_dict):
    wx_friend = Get_Friend(login_info, web_request_base_dict)
    friend_list = wx_friend.get_friend_list()
    
    while 1:
        try:
            wx_receive = Receive_Msg(login_info, web_request_base_dict, friend_list)
            wx_receive.receive()
            get_friend = Get_Friend(login_info, web_request_base_dict , friend_list=friend_list)
            friend_list = get_friend.update_friend_list()
            
            if int(time.time()) % 120 <= 5 :
                try:
                    login = Login(web_request_base_dict, login_info=login_info)
                    check_login = login.check_login()
                    run_time = (int(time.time()) - int(starttime)) // 60
                    if check_login['Ret'] == 0 :
                        print('登陆中，已经登陆了' + str(run_time) + '分钟')
                    else :
                        print('微信号被退出，保持登陆' + str(run_time) + '分钟，请重新执行程序')
                        print(check_login)
                        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
                        break
                        exit(0)
                except :
                    pass
        except :
            pass
            
        time.sleep(5)

receive_thread = threading.Thread(target=receive_func, args=(login_info, web_request_base_dict))
receive_thread.start()

def input_func():
    while 1 :
        try:
            wx_send = Send_Msg(login_info, web_request_base_dict)
            string = input("\n请输入需要发送的信息: \n")
            if string :
                content = time.strftime(' %Y-%m-%d %H:%M:%S', time.localtime()) + '   ' + string
                status = wx_send.send(content)
                if not status :
                    print('微信号被退出')
                    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
                    break
                    exit(0)
        except :
            pass
            
        time.sleep(1)
        
input_thread = threading.Thread(target=input_func)
input_thread.start()

def checklogin_func(web_request_base_dict, login_info):
    while 1 :
        try:
            login = Login(web_request_base_dict, login_info=login_info)
            check_login = login.check_login()
            if check_login['Ret'] == 0 :
                print('OK')
                print(time.strftime(' %Y-%m-%d %H:%M:%S', time.localtime()))
            else :
                print('微信号被退出，请重新登录！')
                print(check_login)
                print(time.strftime(' %Y-%m-%d %H:%M:%S', time.localtime()))
                exit(0)
        except :
            pass
        
        time.sleep(60)
        
# checklogin_thread = threading.Thread(target=checklogin_func, args=(web_request_base_dict, login_info))
# checklogin_thread.start()
