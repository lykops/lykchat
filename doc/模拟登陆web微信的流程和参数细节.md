# 登陆准备阶段

## 微信首页
	get
	https://wx.qq.com
    提供headers
    用途：获取cookie
    后续访问必须带headers、cookie参数

## 获取二维码uuid
	get
	https://wx.qq.com/jslogin
    get参数分别是
        appid：值为自定义，格式为wx782c26e4c19acffb
        fun：值为new
        lang：值为en_us
        redirect_uri：值为https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage
        _：值为当前时间戳
    完整的URL例子https://wx2.qq.com/jslogin?redirect_uri=https%3A%2F%2Fwx.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&appid=wx782c26e4c19acffb&lang=en_US&_=1485065568&fun=new
    用途：获取二维码uuid

## 下载和展示二维码
	get
	https://wx.qq.com/qrcode/{{uuid}}
    例子:https://wx2.qq.com/qrcode/AfdK5U5qyw==

## 扫码和确认
	访问https://wx.qq.com/cgi-bin/mmwebwx-bin/login
    get参数
        loginicon：值必须为true
        uuid：值为{{uuid}}
        r：值为当前时间戳/1524
        _：值为当前时间戳
    完整的URL例子：https://wx2.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid=AacJ62nlRg==&tip=0&r=-974452&_=1485065779
    用途：返回登陆状态，登陆成功之后的redirect_uri
    返回状态码说明如下：
        200，扫码和确认成功
        201，扫码，未确认
        其他，未扫码或者其他原因

# 登陆初始化和获取登陆信息

## 登陆初始化
	get
	{{redirect_uri}}
    完整的URL例子：https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage?ticket=A0k1PKCiAX8_8nyisAG0R9d5@qrticket_0&uuid=AacJ62nlRg==&lang=en_US&scan=1485065793
    用途：返回登陆认证等信息，一个字典类型的json格式，下文用login_info表示

## 获取登陆信息
	post
	https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=【当前时间戳】
    post参数为
        BaseRequest：通过1返回参数获取值
        例子：{"BaseRequest": {"DeviceID": "uKUD8e%2Bp7iXqNpbOuPTntL7OdbsfxEv5JdQjKtb7Mc%2FVQK2leE%2BRrNVkI5fQZZjB", "Sid": "xkQE8IoFPjwXEf2W", "Uin": "575635712", "Skey": "@crypt_2b05caf0_2290c785d1bc5646d2ff0ff771ec3324", "isgrayscale": "1"}}
    用途：返回微信用户信息、第一页好友信息、和BaseRequest、最新聊天信息等等


# 获取好友信息

    get
	https://wx.qq.com/webwxgetcontact
    get参数
        r：值为当前时间戳
        seq：值为0
        skey：值为login_info[Skey]
    完整的URL例子：https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?r=1485065800&seq=0&skey=@crypt_2b05caf0_2290c785d1bc5646d2ff0ff771ec3324
    用途：返回所有的好友信息，字典json格式
    有用的好友信息字段说明：
        Sex：1表示男，2表示女，0为其他【没有设置性别的好友、公众号、群、系统账号等等】
        UserName，微信系统为每个微信号分配一个唯一号码，开头@@表示群、字母或者数字开头表示系统账号，其他【公众号、好友等】以单@开头
        NickName，个人设置的昵称，重复可能性很大
        Alias，微信号，如果没有设置为空，不会出现重复
        
# 接受信息

## 定时检查是否有新信息
        get
		https://{{sync_url}}/synccheck
        get参数是：
            'r'        : 当前时间戳*1000
            'skey'     : login_info[skey]
            'sid'      : login_info[sid]
            'uin'      : login_info[uin]
            'deviceid' : login_info[deviceid]
            'synckey'  : login_info[synckey]
            '_'        : 当前时间戳*1000
        完整的URL例子：https://webpush.wx2.qq.com/cgi-bin/mmwebwx-bin/synccheck?deviceid=e565817597249768&synckey=List_%5B%7B%27Key%27%3A+1%2C+%27Val%27%3A+645531166%7D%2C+%7B%27Key%27%3A+2%2C+%27Val%27%3A+645531276%7D%2C+%7B%27Key%27%3A+3%2C+%27Val%27%3A+645531125%7D%2C+%7B%27Key%27%3A+1000%2C+%27Val%27%3A+1485058018%7D%5D%7CCount_4&skey=%40crypt_2b05caf0_2290c785d1bc5646d2ff0ff771ec3324&sid=xkQE8IoFPjwXEf2W&r=1485065802608&_=1485065802608&uin=575635712    
        用途：返回最新信息数，0表示没有新消息
## 获取新信息内容
		post
		https://wx.qq.com/webwxsync?sid=login_info[sid]&skey=login_info[skey]&lang=en_US&pass_ticket=login_info[pass_ticket]
        post参数为
            'BaseRequest' : login_info[BaseRequest]
            'SyncKey'     : login_info[SyncKey]
            'rr'          :~当前时间戳*1000
            例子：{"rr": -1485065809, "BaseRequest": {"Ret": 0, "ErrMsg": ""}, "SyncKey": {"List": [{"Key": 1, "Val": 645531166}, {"Key": 2, "Val": 645531278}, {"Key": 3, "Val": 645531125}, {"Key": 11, "Val": 645531260}, {"Key": 13, "Val": 645524153}, {"Key": 201, "Val": 1485065810}, {"Key": 203, "Val": 1485064747}, {"Key": 1000, "Val": 1485058018}, {"Key": 1001, "Val": 1485057992}, {"Key": 1002, "Val": 1485058221}, {"Key": 1004, "Val": 1484911834}], "Count": 11}}
        完整的URL例子：https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsync?sid=xkQE8IoFPjwXEf2W&skey=@crypt_2b05caf0_2290c785d1bc5646d2ff0ff771ec3324&lang=en_US&pass_ticket=uKUD8e%2Bp7iXqNpbOuPTntL7OdbsfxEv5JdQjKtb7Mc%2FVQK2leE%2BRrNVkI5fQZZjB
        用途：返回最新信息列表
        注意：群信息的发送者放在Content开头部分

# 发送信息

    post
	https://wx.qq.com/webwxsendmsg
    post参数
            'BaseRequest': self.base_request,
            'Msg': {
                'Type': login_info[BaseRequest],
                'Content': content,
                'FromUserName': 自己的username,
                'ToUserName': 发送的username,
                'LocalID': int(time.time() * 1000 * 1000 * 10),
                'ClientMsgId': int(time.time() * 1000 * 1000 * 10),
                },
            'Scene' : 0
        返回发送结果json字典

![web页面登陆微信的流程](https://raw.githubusercontent.com/lykops/lykchat/master/doc/web页面登陆微信的流程.jpg)