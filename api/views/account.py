#!/usr/bin/env python
# -*- coding:utf-8 -*-

from rest_framework.views import APIView
from rest_framework.response import Response

import uuid

from api.models import *
from api.utils.response import BaseResponse


class LoginView(APIView):
    authentication_classes = []
    def post(self, request, *args, **kwargs):
        ret = BaseResponse()
        username = request.data.get('username')
        password = request.data.get('password')
        try:
            user_obj = Account.objects.get(username=username, password=password)
            token = str(uuid.uuid4())
            ret.data = token
            # 每登陆成功一次就更新一下token值
            UserAuthToken.objects.update_or_create(user=user_obj, defaults={'token': token})
        except Exception as e:
            ret.code = 1001
            ret.error = '用户名或密码错误'
        return Response(ret.__dict__)