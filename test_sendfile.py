import os, random, sys, requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

url = 'http://127.0.0.1/sendmsg'
argvstr = sys.argv[1:]
argv_dict = {}
for argv in argvstr :
    argv = str(argv).replace("\r\n" , "")
    DICT = eval(argv)
    argv_dict.update(DICT)

# 例子/usr/local/python36/bin/python3 /opt/lykchat/test_upload.py "{'username':'zabbix','pwd':'123456','type':'img','friendfield':'1','friend':'lyk-ops','content':'恭喜发财','file':'/root/b.jpg'}"
# # curl -F "file=@/root/a" 'http://127.0.0.1/sendmsg?username=zabbix&pwd=123456&type=img&friendfield=1&friend=lyk-ops&content=test'

parameter_dict = {
    'username' : '用户' ,
    'pwd' : '接口密码，注意不等于登陆密码' ,
    'type' : '发送信息类型，{"txt":"纯文字" ,"img":"图片","file":"发送文件","video":"视频"}，可以为空，默认：没有文件为txt，有文件为file',
    'friendfield':'接受者的字段代号，{0:"NickName" , 1:"Alias" , 2:"RemarkName"}，可以为空，默认为0',
    'friend':'接受者的昵称、微信号、备注名的其中一个，不能为空',
    'content':'发送内容，不能为空',
    'file':'文件绝对路径，可以为空',
    '例子':
        '''
        /usr/local/python36/bin/python3 /opt/lykchat/test_sendfile.py "{'username':'zabbix','pwd':'123456','type':'img','friendfield':'1','friend':'lyk-ops','content':'恭喜发财','file':'/root/b.jpg'}"
        '''
    }

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0',
    'Referer': url
    }

for key in ['username', 'pwd', 'friend', 'content'] :
    if key not in argv_dict :
        print(parameter_dict)
        exit(0)

if 'file' not in argv_dict :
    data = argv_dict
    r = requests.post(url, data=data, headers=headers)
    print(r.text)
    exit(0)

multipart_encoder = MultipartEncoder(
    fields={
        'username': argv_dict['username'],
        'pwd': argv_dict['pwd'],
        'type': 'txt',
        'friendfield': argv_dict['friendfield'],
        'friend': argv_dict['friend'],
        'content': argv_dict['content'],
        'file': (os.path.basename(argv_dict['file']) , open(argv_dict['file'], 'rb'), 'application/octet-stream')
        },
        boundary='-----------------------------' + str(random.randint(1e28, 1e29 - 1))
    )

headers['Content-Type'] = multipart_encoder.content_type
# multipart/form-data

r = requests.post(url, data=multipart_encoder, headers=headers, timeout=300)
print(r.text)
