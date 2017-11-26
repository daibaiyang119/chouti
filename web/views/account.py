#!/usr/bin/env python
# -*- coding:utf-8 -*-
import io
import json
import datetime

from django.shortcuts import HttpResponse, redirect, render

from web.forms.account import SendMsgForm, RegisterForm, LoginForm
from web import models

from backend import commons
from backend.utils import check_code as CheckCode
from backend.utils.response import BaseResponse
from backend.utils.message import send_email
from django.db.models import F, Q


def check_code(request):
    """
    获取验证码
    :param request:
    :return:
    """
    stream = io.BytesIO()
    # 创建随机字符 code
    # 创建一张图片格式的字符串，将随机字符串写到图片上
    img, code = CheckCode.create_validate_code()
    img.save(stream, "PNG")
    # 将字符串形式的验证码放在Session中
    request.session["CheckCode"] = code
    return HttpResponse(stream.getvalue())


def send_msg(request):
    """发送邮件验证码"""
    rep = BaseResponse()
    form = SendMsgForm(request.POST)
    # 一、先检查邮箱格式
    if form.is_valid():
        _value_dict = form.clean()
        email = _value_dict["email"]

        # 二、再检查邮箱是否已被注册
        has_exists_email = models.UserInfo.objects.filter(email=email).count()
        if has_exists_email:
            rep.summary = "此邮箱已被注册"
            return HttpResponse(json.dumps(rep.__dict__))

        # 三、再检查此邮箱发送验证码的次数，并生成当前时间以及验证码
        current_date = datetime.datetime.now()
        code = commons.random_code()
        count = models.SendMsg.objects.filter(email=email).count()

        if not count:
            # 如果此邮箱从没有发送过验证码，则在数据库SendMsg表创建一条新记录，并发送邮件
            models.SendMsg.objects.create(code=code, email=email, ctime=current_date, times=1)
            rep.status = True
            # 发送邮件
            send_email(email, "验证码：" + str(code))
        else:
            # 如果之前发送过验证码，先检查有没有超过限制，一小时只能发10次
            limit_time = current_date - datetime.timedelta(hours=1)
            current_times = models.SendMsg.objects.filter(email=email, ctime__gt=limit_time, times__gt=9).count()
            if current_times:
                # 如果已经发送超过9次，并且最后一次发邮件到现在还没有超过一小时，提示错误，等待一小时后重试
                rep.summary = "已超过最大次数，请一小时后重试"
            else:
                # 如果最后一次发送邮件时间到现在已经超过一小时了，则将计数归零，重新计算
                # 然后更新数据库记录
                unfreeze = models.SendMsg.objects.filter(email=email, ctime__lt=limit_time).count()
                if unfreeze:
                    models.SendMsg.objects.filter(email=email).update(times=0)
                models.SendMsg.objects.filter(email=email).update(code=code, ctime=current_date, times=F("times")+1)
                rep.status = True
                # 发送邮件
                send_email(email, "验证码：" + str(code))
    else:
        rep.summary = form.errors["email"][0]
    return HttpResponse(json.dumps(rep.__dict__))


def register(request):
    """用户注册"""
    rep = BaseResponse()
    form = RegisterForm(request.POST)
    if form.is_valid():
        # 如果格式正确，先检查验证码是否匹配或过期
        _value_dict = form.clean()
        current_date = datetime.datetime.now()
        limit_date = current_date - datetime.timedelta(minutes=5)
        is_valid_code = models.SendMsg.objects.filter(ctime__gt=limit_date,
                                                      email=_value_dict["email"],
                                                      code=_value_dict["email_code"])
        # 如果没有匹配的记录，则表示验证码错误或过期
        if not is_valid_code:
            rep.message["email_code"] = "验证码错误或已过期"
            return HttpResponse(json.dumps(rep.__dict__))

        # 防止注册过程中修改邮箱，再次验证邮箱是否已注册
        has_exists_email = models.UserInfo.objects.filter(email=_value_dict["email"]).count()
        if has_exists_email:
            rep.message["email"] = "邮箱已注册"
            return HttpResponse(json.dumps(rep.__dict__))

        # 检查用户名是否已存在
        has_exists_username = models.UserInfo.objects.filter(username=_value_dict["username"]).count()
        if has_exists_username:
            rep.message["username"] = "用户名已存在"
            return HttpResponse(json.dumps(rep.__dict__))

        # 修改_value_dict字典信息，通过字典直接创建用户信息
        _value_dict["ctime"] = current_date
        _value_dict.pop("email_code")
        obj = models.UserInfo.objects.create(**_value_dict)
        user_info_dict = {"nid": obj.nid, "username": obj.username, "email": obj.email}

        # 删除SendMsg表中的记录
        models.SendMsg.objects.filter(email=_value_dict["email"]).delete()

        # 设置session，保存用户登录状态
        request.session["is_login"] = True
        request.session["user_info"] = user_info_dict

        rep.status = True

        # 发送邮件通知注册成功
        send_email(_value_dict["email"], "恭喜您注册成功!")
    else:
        # 如果格式不正确，则返回错误信息
        # 先将错误信息转换成字符串，再转换成字典
        error_str = form.errors.as_json()
        rep.message = json.loads(error_str)
    return HttpResponse(json.dumps(rep.__dict__))


def login(request):
    """用户登录"""
    rep = BaseResponse()
    form =LoginForm(request.POST)
    if form.is_valid():
        # 先检查图形验证码是否匹配
        _value_dict = form.clean()
        if _value_dict["code"].lower() != request.session["CheckCode"].lower():
            rep.message = {"code": [{"message": "验证码错误"}]}

        # 如果验证码正确，数据库中匹配用户名&密码或邮箱&密码
        con = Q()
        q1 = Q()
        q1.connector = "AND"
        q1.children.append(("email", _value_dict["user"]))
        q1.children.append(("password", _value_dict["pwd"]))

        q2 = Q()
        q2.connector = "AND"
        q2.children.append(("username", _value_dict["user"]))
        q2.children.append(("password", _value_dict["pwd"]))

        con.add(q1, "OR")
        con.add(q2, "OR")

        obj = models.UserInfo.objects.filter(con).first()
        if not obj:
            rep.message = {"user": [{"message": "用户名邮箱或密码错误"}]}
            return HttpResponse(json.dumps(rep.__dict__))

        # 如果验证正确，设置session
        request.session["is_login"] = True
        request.session["user_info"] = {'nid': obj.nid, 'email': obj.email, 'username': obj.username}

        rep.status = True
    else:
        error_str = form.errors.as_json()
        rep.message = json.loads(error_str)
    return HttpResponse(json.dumps(rep.__dict__))


def logout(request):
    """用户退出"""
    request.session.clear()
    return redirect("/index.html")