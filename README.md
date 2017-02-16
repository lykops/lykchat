# lykchat
lykchat模拟微信网页端，在web页面、命令行上进行微信登陆、接受和发送信息等操作，web界面还提供一个发送信息接口。


web界面已实现的功能说明：

	1、web界面
		实现扫码登陆、显示登陆状态、选择好友发送信息等功能；
		并通过session共享机制，共享微信登陆状态信息，在任何地方访问保持信息一致；
	2、计划任务定时检查登陆状态和接受最新信息；
	3、发送信息接口（web界面）为其他应用提供给微信好友发送信息的功能。
		发送接口URL地址为http://IP或者域名/sendmsg，
		post和get方法均可
		请求参数说明：
			friendfield：接受者的字段代号，{0:"NickName" , 1:"Alias" , 2:"RemarkName"}，可以为空，默认为0 
			friend：接受者的昵称、别名、备注名的其中一个，不能为空
			content：发送内容，不能为空
		例子：http://192.168.100.104/sendmsg?friendfield=1&friend=lyk-ops&content=测试
		执行之后返回一个json格式的字典，包含发送结果代码【0为成功，其他均失败】，发送失败原因、好友信息等等

截图：
![等待扫码 截图](https://github.com/lykops/lykchat/blob/master/doc/等待扫码.jpg)
等待扫码 截图

![二维码已失效 截图](https://github.com/lykops/lykchat/blob/master/doc/二维码已失效.jpg)
二维码已失效 截图

![登陆成功之后 截图](https://github.com/lykops/lykchat/blob/master/doc/登陆成功之后.jpg)
登陆成功之后 截图

![发送信息截图 截图](https://github.com/lykops/lykchat/blob/master/doc/发送信息截图.jpg)
发送信息截图 截图

![好友列表截图 截图](https://github.com/lykops/lykchat/blob/master/doc/好友列表截图.jpg)
好友列表截图 截图

![接口发送信息 截图](https://github.com/lykops/lykchat/blob/master/doc/接口发送信息.jpg)
接口发送信息 截图


命令行已实现的功能说明：

	扫码登陆、显示登陆状态、接受好友信息、发送信息（目前只能发送给“文件传输助手”）

项目说明：

	1、由于本人专业水平有限，该项目很可能有bug，请与我联系。
		微信号：lyk-ops
	2：该项目为个人开源项目，免费提供使用。
		在使用过程中，如有任何问题，本人不承担任何责任。
	3、该项目开发的目的：为监控系统提供一个通过微信发送告警信息。
		所以该项目只实现了微信的登陆、接受和发送信息这三个功能，其他功能暂不考虑。
	4、该项目是基于微信web端进行开发的，
		微信公众号只能展示订阅号，无法展示企业号和服务号，而且无法向公众号发送信息。
		由于微信web端接口参数经常变动，可能会导致系统异常。
		如本人发现该问题，将会更新和修复。

已知事项：

	1、web界面和命令行的登陆信息无法共享。
	2、在该版本中，web界面只允许一个微信登陆。
	3、关于web页面选择好友部分群无法展示说明：
		由于微信web端的好友清单中没有展示群，显示的群是通过第一页活跃好友展示。
		如果需要获取这些群名称的话，你可以在这个群里发条信息就可以看到了。

下个版本实现的功能：

	1、设置登陆账号和密码
	2、web界面运行多个微信号登陆
	3、完善功能和修复bug
	4、.....
	


运行环境说明：

	操作系统：Linux和Windows，测试环境为CentOS 7（最新版即可）
	语言环境：Python3+django1.10，测试环境使用Python3.5.2、3.6.0两个版本测试
	web服务器：Nginx，主要解决静态文件展示。测试环境为nginx 1.10.2
	数据库：MySQL，用于存储缓存。测试环境为5.7.17
	

![安装步骤请见wiki](https://github.com/lykops/lykchat/wiki/%E5%AE%89%E8%A3%85%E6%AD%A5%E9%AA%A4)