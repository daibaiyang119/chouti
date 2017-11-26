#!/usr/bin/env python
# -*- coding:utf-8 -*-


import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr


def send_email(email_list, content, subject="抽屉新热榜-用户注册"):
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = formataddr(["Administrator", "18217467310@139.com"])
    msg['Subject'] = subject
    # SMTP服务
    server = smtplib.SMTP("smtp.139.com", 25)
    server.login("18217467310@139.com", "dby123456")
    server.sendmail('18217467310@139.com', email_list, msg.as_string())
    server.quit()


