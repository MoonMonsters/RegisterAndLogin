#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Flynn on 2018-02-04 15:17
import os
from django.core.mail import send_mail, EmailMultiAlternatives

os.environ['DJANGO_SETTINGS_MODULE'] = 'RegisterAndLogin.settings'

if __name__ == '__main__':
	# send_mail(
	# 	'来自flynngod@sina.com的问候',
	# 	'恭喜你接收到我的第一封邮件',
	# 	'flynngod@sina.com',
	# 	['qxinhai@qq.com', 'qxinhai@yeah.net']
	# )

	subject, from_email, to = '来自flynngod@sina.com的问候', 'flynngod@sina.com', 'qxinhai@yeah.net'
	text_content = '恭喜你接收到我的第一封邮件'
	html_content = '<p><a href="http://127.0.0.1:8000/login/index" target=blank>访问主页</a></p>'
	msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
	msg.attach_alternative(html_content, 'text/html')
	msg.send()
