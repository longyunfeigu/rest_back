#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json

from rest_framework.views import APIView
from django_redis import get_redis_connection
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from api.models import *
from api.utils.response import BaseResponse
from api.utils.convert import regular
from api.utils.exception import PricePolicyInvalid

class ShoppingCarView(APIView):
    """购物车API"""
    conn = get_redis_connection('default')
    def get(self, request, *args, **kwargs):
        """获取用户个人的购物车信息"""
        ret = BaseResponse()
        total = 0
        lis = []
        try:
            key_match = settings.SHOPPING_CAR_KEY%(request.user.id, '*')

            for item in self.conn.scan_iter(key_match, count=10):
                total += 1
                redis_value = self.conn.hgetall(item)
                lis.append(regular(redis_value))

            ret.data = {'total':total, 'myShopCart':lis}
        except Exception as e:
            ret.code = 1004
            ret.error = '获取购物车信息失败'
        return Response(ret.__dict__)

    def post(self, request, *args, **kwargs):
        """创建一条购物车信息"""
        ret = BaseResponse()
        try:
            courseId = int(request.data.get('courseId'))
            course_obj = Course.objects.get(pk=courseId)
            policy_id = int(request.data.get('policy_id'))
            redis_key = settings.SHOPPING_CAR_KEY%(request.user.id, courseId)
            policy = {}
            for item in course_obj.price_policy.all():
                policy[item.id] = {'name':item.get_valid_period_display(),'price':item.price}

            if policy_id not in policy:
                raise PricePolicyInvalid('价格策略不合法')
            redis_value = {'title':course_obj.name,
                           'image':course_obj.course_img,
                           'policy':json.dumps(policy),
                           'default_policy': policy_id}
            if self.conn.exists(redis_key):
                ret.data = '购物车中该套餐已更新成功'
            else:
                ret.data = '添加到购物车成功'
            self.conn.hmset(redis_key, redis_value)
        except PricePolicyInvalid as e:
            ret.code = 2001
            ret.error = e.msg
        except ObjectDoesNotExist as e:
            ret.code = 2002
            ret.error = '课程不存在'
        except Exception as e:
            ret.code = 2003
            ret.error = '获取购物车失败'
        return Response(ret.__dict__)

    def put(self, request, *args, **kwargs):
        """更新购物车信息"""
        ret = BaseResponse()
        try:
            course_id = request.data.get('courseId')
            policy_id = request.data.get('policy_id')
            redis_key = settings.SHOPPING_CAR_KEY%(request.user.id, course_id)
            policy_dict = json.loads(str(self.conn.hget(redis_key, 'policy'), encoding='utf-8'))
            if policy_id not in policy_dict:
                raise PricePolicyInvalid('价格策略不合法')
            self.conn.hset(redis_key, 'default_policy', policy_id)
            ret.data = '更新成功'
        except PricePolicyInvalid as e:
            ret.code = 2001
            ret.error = e.msg
        except Exception as e:
            ret.code = 2004
            ret.error = '修改失败'
        return Response(ret.__dict__)

    def delete(self, request, *args, **kwargs):
        """删除购物车信息"""
        ret = BaseResponse()
        try:
            keys = [settings.SHOPPING_CAR_KEY%(request.user.id, i) for i in request.data]
            self.conn.delete(*keys)
            ret.data = '删除成功'
        except Exception as e:
            ret.code = 3001
            ret.error = '删除失败'
        return Response(ret.__dict__)