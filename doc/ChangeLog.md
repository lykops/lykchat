# V2.1.0
## 升级内容
	新增发送图片、视频、文件等多媒体信息
## 从v2.0.0更新步骤
	1、下载最新版本
	2、安装依赖包
		/usr/local/python36/bin/pip3 install -r /opt/lykchat/install/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
	3、修改配置文件
		配置文件library/config/wechat.py
		新增上传文件最大数max_upload_size（默认为5M，建议不要上传文件太大，导致访问接口超时）
	4、修改nginx的上传文件最大值
		client_max_body_size  10m;
## 说明事项
	django默认启用防CSRF（Cross-site request forgery跨站请求伪造），导致无法使用post方法调用该接口，所以作者强制关闭了防csrf功能。
	如果你觉得有安全隐患，又不需要发送多媒体文件，请下载2.0版本：https://codeload.github.com/lykops/lykchat/zip/master  

# V2.0.0
	
	1、修复bug：
		微信登陆时间超过12小时自动退出，测试过程中测得最大登陆时长20天
	2、完善功能：
		1）、微信会话保持机制：
			保存位置：之前保存在数据库中，修改为数据库只记录用户名，所有信息保持到文件中，减少数据库的查询、写入、加解密压力
			动态更新微信登陆信息
			调整会话信息内容
		2）、优化微信检测登陆流程，大大缩短各个页面执行时间
		3）、完善获取好友流程
	3、新增功能：
		1）、增加用户管理机制
		2）、好友信息缓存机制
	4、取消功能：
		接受和处理新信息