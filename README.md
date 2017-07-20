# lykchat信息发送系统
lykchat信息发送系统是Python3开发的，通过模拟微信网页端，基于个人微信号，为系统管理人员提供信息发送工具。

实现的功能有用户登录管理、微信登陆管理和微信信息发送功能。


# 注意
在2017年7月20日晚上，疑似微信web端做了调整，web上不在显示好友微信号，所以即日使用微信号发送信息可能提示无法找到好友等错误提示。

解决办法：
        1、使用好友昵称来发送信息
        2、使用备注名来发送信息
	但必须只能是数字、字母、符号等，不能为图片等

## 特点

	1、简单高效
		基于个人微信号，模拟微信web端，部署和维护简单
		web管理页面实现可视化管理微信登陆
		接口采用URL，简化调用复杂度，返回结果均为json格式
	2、信息共享 
		通过共享用户session和微信登陆信息，保证系统长期稳定运行 
	3、7*24不间断服务
		计划任务定时检查微信登陆状态，微信保持登陆超过20天
	4、支持发送多媒体信息
		除了支持发送纯文字信息外，还支持发送图片、视频、文件等信息
	5、用户管理
		通过用户隔离微信个人号，不同用户管理不同微信号
		用户密码分为管理密码和接口密码，保证用户信息安全性
	6、微信信息安全
		不会监控和存储微信聊天信息
		不会增加和删除好友


## 截图

管理页面--功能展示

![等待扫码 截图](https://raw.githubusercontent.com/lykops/lykchat/master/doc/web页面--功能说明.jpg)


管理页面--微信登陆时长

![微信登陆时长 截图](https://raw.githubusercontent.com/lykops/lykchat/V2.1.0/doc/微信登陆时间超过1天.jpg)
 
接口-发送信息成功

![发送信息成功 截图](https://raw.githubusercontent.com/lykops/lykchat/master/doc/接口-发送信息成功.jpg)
 
	
## 发送信息接口使用说明
[https://github.com/lykops/lykchat/wiki/%E5%8F%91%E9%80%81%E4%BF%A1%E6%81%AF%E6%8E%A5%E5%8F%A3%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E](https://github.com/lykops/lykchat/wiki/%E5%8F%91%E9%80%81%E4%BF%A1%E6%81%AF%E6%8E%A5%E5%8F%A3%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E "发送信息接口")

## 模块和工作流程
[https://github.com/lykops/lykchat/wiki/%E6%A8%A1%E5%9D%97%E5%92%8C%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%A8%8B](https://github.com/lykops/lykchat/wiki/%E6%A8%A1%E5%9D%97%E5%92%8C%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%A8%8B "模块和工作流程")

## 安装手册
[https://github.com/lykops/lykchat/wiki/%E5%AE%89%E8%A3%85%E6%89%8B%E5%86%8C](https://github.com/lykops/lykchat/wiki/%E5%AE%89%E8%A3%85%E6%89%8B%E5%86%8C "安装手册")

## ChangeLog
[https://github.com/lykops/lykchat/wiki/ChangeLog](https://github.com/lykops/lykchat/wiki/ChangeLog "ChangeLog")
 
## 说明

	1、作者尽可能通过严谨测试来验证系统功能，但由于专业水平有限，无法避免出现bug。
	2、该项目是基于微信web端进行开发的
		由于微信web端参数经常变动，可能会导致系统异常。
		如作者发现该问题，将会更新和修复。
	3、该项目开发的目的：为监控系统提供一个通过微信发送告警信息。
		所以该项目只实现了微信的登陆、接受和发送信息这三个功能，其他功能暂不考虑。
		建议使用一个独立的微信号，避免在登陆过程中在微信web端、PC客户端登陆，也不要在手机端退出web登陆。
	4：该项目为个人开源项目，免费开源。
		请勿使用该系统发送非法、不良信息。
		在使用过程中，如有任何问题，作者不承担任何责任。
	5、联系方式：		
		微信：lyk-ops
		邮箱：liyingke112@126.com	


