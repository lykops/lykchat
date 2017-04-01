import os, platform
from lykchat.settings import BASE_DIR

version = '2.0.0'
base_url = 'https://wx2.qq.com'
os_type = platform.system()  # Windows, Linux, Darwin
curr_dir = os.getcwd()
qr_dir = BASE_DIR + '/static/qr'
appid = 'wx782c26e4c19acffb'
# 微信appid

user_mess_dict = {
        'lykchat' : {'login_pwd' : 'lykchat', 'interface_pwd' : '123456'},
        'zabbix' : {'login_pwd' : 'zabbix', 'interface_pwd' : '123456'},
        'test' : {'login_pwd' : 'test', 'interface_pwd' : '123456'},
    }
# web账号信息，login_pwd用于web端登陆密码，interface_pwd用于接口发送信息密码

login_status_code_dict = {
    100 : {'descript':'空空如也', 'suggest':'正在初始化，请稍后！如果你等待很久，请刷新页面', 'status': 100},
    101 : {'descript':'初始化完毕', 'suggest':'请扫二维码，如已扫码请刷新页面', 'status': 101},
    102 : {'descript':'等待扫码', 'suggest':'请扫二维码，如已扫码请刷新页面', 'status': 102},
    200 : {'descript':'确认登陆', 'suggest':'请刷新页面', 'status': 200},
    201 : {'descript':'扫码成功', 'suggest':'请刷新页面', 'status': 201},
    202 : {'descript':'等待扫码', 'suggest':'请扫二维码，如已扫码请刷新页面', 'status': 202},
    221 : {'descript':'登陆初始化完成', 'suggest':'请刷新页面', 'status': 221},
    222 : {'descript':'保持登陆', 'suggest':'可以发送信息', 'status': 222},
    400 : {'descript':'未知原因退出登陆', 'suggest':'未知原因退出登陆，请重新登陆', 'status': 400},
    401 : {'descript':'被微信强制退出', 'suggest':'请重新登陆，请重新登录！如果多次如此，可能是微信修改了接口，请联系开发者', 'status': 401},
    402 : {'descript':'手机端退出登陆', 'suggest':'请重新登陆', 'status': 402},
    403 : {'descript':'该微信号人为禁止登陆', 'suggest':'该微信号人为禁止登陆', 'status': 403},
    404 : {'descript':'可能被拉黑', 'suggest':'如果多次出现这个情况，被服务器拉黑，等几个小时在登陆吧，或者换个微信', 'status': 404},
    408 : {'descript':'二维码已失效', 'suggest':'请刷新页面', 'status': 408},
    444 : {'descript':'web页面退出登陆', 'suggest':'请重新登陆', 'status': 444},
    500 : {'descript':'被拉黑了', 'suggest':'无人道，又被拉黑！等几个小时在登陆把，或者换个微信吧', 'status': 500},
    }
# 200、201、408属于微信自定义状态，其他自定义的

language = 'Chinese'
sendresult_translation_dict = {
    'Chinese': {
        - 1000: u'返回值不带BaseResponse',
        - 1001: u'没有找到接受者',
        - 1002: u'文件位置错误',
        - 1003: u'服务器拒绝连接',
        - 1004: u'服务器返回异常值',
        - 1005: u'参数错误',
        - 1006: u'未知错误',
        1201: u'该微信不存在',
        1101: u'微信退出登录',
        1204: u'疑似原因：可能是自己的微信号',
        0: u'发送成功',
    },
}

DATABASES = {
    'default': {
        'ENGINE' : 'django.db.backends.mysql',
        'NAME' : 'lykchat',
        'USER' : 'lykchat',
        'PASSWORD' :'!QAZ2wsx',
        'HOST' : '127.0.0.1',
        'PORT' : '3306',
        'OPTIONS': {  
            'charset': 'utf8',
            'use_unicode': True,
        },
    },
}


SESSION_COOKIE_AGE = 60 * 60 * 1


CRONJOBS = (
    ('*/2 * * * *', 'library.cron.checklogin.check_login', '>>/dev/shm/lykchat.txt 2>&1'),
)


url_frond = 'http://127.0.0.1/'

friendlist_field_list = ['UserName', 'NickName', 'Alias', 'Sex', 'RemarkName']
'''
UserName，每个好友的唯一标示
NickName，个人设置的昵称，重复可能性很大
Alias，微信号，如果没有设置为空，不会出现重复
RemarkName 好友备注名字
RemarkPYQuanPin , 好友备注名字全拼
RemarkPYInitial，好友备注名字拼音缩写
'''
