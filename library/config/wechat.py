import os
from lykchat.settings import BASE_DIR

base_url = 'https://wx2.qq.com'
curr_dir = os.getcwd()
qr_dir = BASE_DIR + '/static/qr'
appid = 'wx782c26e4c19acffb'
        # 微信appid，是微信端指定的，不要随意修改
curr_dir = os.getcwd()
        
login_status_code_dict = {
    100 : {'descript':'空空如也', 'suggest':'正在初始化请稍后，如你等待很久请刷新', 'status': 100},
    101 : {'descript':'初始化完毕', 'suggest':'请扫二维码，如已扫码请刷新页面', 'status': 101},
    102 : {'descript':'等待扫码', 'suggest':'请扫二维码，如已扫码请刷新页面', 'status': 102},
    200 : {'descript':'确认登陆', 'suggest':'请在手机上确认，如已确认请刷新页面', 'status': 200},
    201 : {'descript':'扫码成功', 'suggest':'请在手机上确认，如已确认请刷新页面', 'status': 201},
    202 : {'descript':'等待扫码', 'suggest':'请扫二维码，如已扫码请刷新页面', 'status': 202},
    221 : {'descript':'登陆初始化完成', 'suggest':'请刷新页面', 'status': 221},
    222 : {'descript':'登陆中', 'suggest':'可以发送信息', 'status': 222},
    400 : {'descript':'未知原因退出', 'suggest':'请重新登陆', 'status': 400},
    401 : {'descript':'被微信强制退出', 'suggest':'请重新登陆', 'status': 401},
    402 : {'descript':'手机端退出登陆', 'suggest':'请重新登陆', 'status': 402},
    403 : {'descript':'该微信号人为禁止登陆', 'suggest':'该微信号人为禁止登陆', 'status': 403},
    404 : {'descript':'可能被微信端拉黑', 'suggest':'如果多次出现，被微信端拉黑，等一段时间再登陆或者换微信号', 'status': 404},
    408 : {'descript':'二维码已失效', 'suggest':'请刷新页面', 'status': 408},
    444 : {'descript':'web页面退出登陆', 'suggest':'请重新登陆', 'status': 444},
    500 : {'descript':'可能被微信端拉黑', 'suggest':'出现在确认登陆前出现说明二维码过期；负责被拉黑，等一段时间再登陆或者换微信号', 'status': 500},
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
        - 9999: u'执行时代码出现异常',
        1201: u'该微信不存在',
        1101: u'微信退出登录',
        1204: u'疑似原因：可能是自己的微信号',
        3 : u'疑似原因：手机端退出超过1天，手机登陆该微信',
        0: u'发送成功',
    },
}
        
max_upload_size = 1024 * 1024 * 5
# 上传文件最大值，单位bytes，默认5M
        
friendlist_field_list = ['UserName', 'NickName', 'Alias', 'Sex', 'RemarkName']
'''
UserName，每个好友的唯一标示
NickName，个人设置的昵称，重复可能性很大
Alias，微信号，如果没有设置为空，不会出现重复
RemarkName 好友备注名字
RemarkPYQuanPin , 好友备注名字全拼
RemarkPYInitial，好友备注名字拼音缩写
'''
