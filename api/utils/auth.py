#!/usr/bin/env python
# -*- coding:utf-8 -*-
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions

from api.models import *

class MyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.query_params.get('token')
        obj = UserAuthToken.objects.filter(token=token).first()
        if obj:
            return (obj.user, token)
        raise exceptions.AuthenticationFailed({'code': 1001, 'error': '认证失败','data':None})