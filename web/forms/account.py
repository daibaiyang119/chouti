#!/usr/bin/env python
# -*- coding:utf-8 -*-

from django import forms


class SendMsgForm(forms.Form):
    email = forms.EmailField()


class RegisterForm(forms.Form):
    username = forms.CharField(min_length=4)
    email = forms.EmailField()
    password = forms.CharField(min_length=6)
    email_code = forms.CharField()


class LoginForm(forms.Form):
    user = forms.CharField(min_length=4)
    pwd = forms.CharField(min_length=6)
    code = forms.CharField()

