import json
import os, random, sys, requests

from requests_toolbelt.multipart.encoder import MultipartEncoder


url = 'http://127.0.0.1/wechat/sendmsg'
argvstr = sys.argv[1:]
argv_dict = {}
for argv in argvstr :
    try :
        argv = argv.split("=")
        argv_dict[argv[0]] = argv[1]
    except :
        pass

parameter_dict = {
    'username' : '用户' ,
    'pwd' : '接口密码，注意不等于登陆密码' ,
    'friend':'接受者的昵称、微信号、备注名的其中一个，不能为空',
    'content':'发送内容，不能为空',
    'file':'文件绝对路径，可以为空',
    'wxid':'发送者的昵称，能为空',
    
    '例子':
        '''
        /usr/local/python36/bin/python3 /opt/lykchat/test_sendfile.py username=zabbix pwd=123456 friend=lykops content=恭喜发财 file=/root/b.jpg
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
    result = r.text
else :
    multipart_encoder = MultipartEncoder(
        fields={
            'username': argv_dict['username'],
            'pwd': argv_dict['pwd'],
            'friend': argv_dict['friend'],
            'content': argv_dict['content'],
            'file': (os.path.basename(argv_dict['file']) , open(argv_dict['file'], 'rb'), 'application/octet-stream')
            },
            boundary='-----------------------------' + str(random.randint(1e28, 1e29 - 1))
        )
    
    headers['Content-Type'] = multipart_encoder.content_type
    # multipart/form-data

    r = requests.post(url, data=multipart_encoder, headers=headers, timeout=300)
    result = r.text
    
result = json.loads(result)
if isinstance(result[1], str) :
    content = result[1].encode() 
    content = content.decode() 
    print(content)
else :
    print(result[1])
        
