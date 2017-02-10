import os, platform
from lykchat.settings import BASE_DIR

version = '1.0.0'
base_url = 'https://wx2.qq.com'
os_type = platform.system()  # Windows, Linux, Darwin
curr_dir = os.getcwd()
qr_dir = BASE_DIR + '/static'

session_type = 'web_wechat_login'
# session类别名称

login_status_code_dict = {
    100 : {'descript':'空空如也', 'suggest':'我正在初始化，请稍后，如果你登陆很久，刷新页面', 'status': 100},
    101 : {'descript':'初始化完毕', 'suggest':'请扫下面的二维码，如已扫码请刷新页面', 'status': 101},
    102 : {'descript':'等待扫码', 'suggest':'请扫下面的二维码，如已扫码请刷新页面', 'status': 102},
    200 : {'descript':'确认登陆', 'suggest':'请刷新页面', 'status': 200},
    201 : {'descript':'扫码成功', 'suggest':'请扫下面的二维码，如已扫码请刷新页面', 'status': 201},
    202 : {'descript':'等待扫码', 'suggest':'请扫下面的二维码，如已扫码请刷新页面', 'status': 202},
    222 : {'descript':'保持登陆', 'suggest':'可以发送信息', 'status': 222},
    400 : {'descript':'未知原因退出登陆', 'suggest':'请刷新页面，可能知道真相', 'status': 400},
    401 : {'descript':'被微信强制退出', 'suggest':'请重新登陆', 'status': 401},
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
