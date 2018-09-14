#!/usr/bin/env python
# -*- coding:utf-8 -*-
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin
from rest_framework.pagination import BasePagination

from api.utils.response import BaseResponse
from api.utils.serializer import *
from api.models import *
from api.utils.pagination import MyLimitOffsetPagination


class NewsView(ViewSetMixin, APIView):
    authentication_classes = []
    def list(self, request, *args, **kwargs):
        ret = BaseResponse()
        try:
            article_list = Article.objects.all()
            paginator = MyLimitOffsetPagination()
            pager_articles = paginator.paginate_queryset(article_list, request, view=self)
            ser = NewsSerializer(instance=pager_articles, many=True)
            response = paginator.get_paginated_response(ser.data)
            ret.data = response
        except Exception as e:
            ret.error = '未获取到资源'
            ret.code = 1001
        return Response(ret.__dict__)
        # return response

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        ret = BaseResponse()
        try:
            article = Article.objects.get(pk=pk)
            ser = SingleNewsSerializer(instance=article, many=False)
            ret.data = ser.data
        except Exception as e:
            ret.error = '未获取到资源'
            ret.code = 1001
        return Response(ret.__dict__)


class AgreeView(APIView):
    def post(self, request, *args, **kwargs):
        aid = request.data.get('aid')
