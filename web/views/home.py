#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import copy
import datetime
import json

from django.shortcuts import render, HttpResponse
from django.db.models import F

from web import models
from web.forms.home import IndexForm

from backend.utils.pager import Pagination
from backend.utils.response import BaseResponse, StatusCodeEnum
from backend import commons
from django import views


def index(request):
    """
    抽屉主页
    :param request:
    :return:
    """
    if request.method == 'GET':
        # 页面分页
        page = request.GET.get('page', 1)
        all_count  = models.News.objects.all().count()
        obj = Pagination(page, all_count)

        result = models.News.objects.all().order_by("-nid").values_list("nid", "title", "url", "content",
                                                                        "ctime", "user_info__username",
                                                                        "news_type__caption",
                                                                        "favor_count",
                                                                        "comment_count",
                                                                        "favor__nid")[obj.start: obj.end]
        print(models.News.objects.all().order_by("-nid").values())
        str_page = obj.string_pager("/index/")
        return render(request, 'index.html', {'str_page': str_page, 'news_list': result})


def favor(request):
    """新闻点赞"""
    rep = BaseResponse()

    news_id = request.POST.get("news_id", None)
    if not news_id:
        rep.summary = "新闻ID不能为空"
    else:
        user_info_id = request.session["user_info"]["nid"]

        has_favor = models.Favor.objects.filter(user_info_id=user_info_id, news_id=news_id).count()
        if has_favor:
            models.Favor.objects.filter(user_info_id=user_info_id, news_id=news_id).delete()
            models.News.objects.filter(nid=news_id).update(favor_count=F("favor_count")-1)

            rep.code = StatusCodeEnum.FavorMinus
        else:
            models.Favor.objects.create(user_info_id=user_info_id, news_id=news_id, ctime=datetime.datetime.now())
            models.News.objects.filter(nid=news_id).update(favor_count=F("favor_count")+1)

            rep.code = StatusCodeEnum.FavorPlus

        # 获取当前点赞数返回给前端
        obj = models.News.objects.get(nid=news_id)
        rep.counts = obj.favor_count

        rep.status = True
    return HttpResponse(json.dumps(rep.__dict__))

