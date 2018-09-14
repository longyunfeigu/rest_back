#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import datetime

from rest_framework.views import APIView
from django.conf import settings
from django_redis import get_redis_connection
from rest_framework.response import Response

from api.utils.response import BaseResponse
from api.models import *

class PaymentView(APIView):
    conn = get_redis_connection('default')
    def get(self, request, *args, **kwargs):
        """获取结算中心数据"""
        ret = BaseResponse()
        user_id = request.user.id
        key_list = self.conn.keys(settings.PAYMENT_KEY % (user_id, '*'))
        course_list = []
        for key in key_list:
            info = {}
            data = self.conn.hgetall(key)
            for k, v in data.items():
                kk = k.decode('utf8')
                if kk == 'coupon':
                    v = json.loads(v.decode('utf8'))
                else:
                    v = v.decode('utf8')
                info[kk] = v
            course_list.append(info)
        pay_global_key = settings.PAYGLOBAL_KEY % user_id
        # global_coupon的值直接使用hgetall(key) 会报错，因为json序列化的时候key必须是str，不能使bytes
        ret.data = {
                'course_list': course_list,
                'global_coupon': {
                    'coupon': json.loads(self.conn.hget(pay_global_key, 'coupon').decode('utf-8')),
                    'default_coupon': self.conn.hget(pay_global_key, 'default_coupon').decode('utf-8')
                }
            }

        return Response(ret.__dict__)

    def patch(self, request, *args, **kwargs):
        """修改结算中心数据"""
        user_id = request.user.id
        ret = BaseResponse()
        course_id = request.data.get('course_id')
        coupon_id = request.data.get('coupon_id')
        payment_key = settings.PAYMENT_KEY % (user_id, course_id)
        payment_global_key = settings.PAYGLOBAL_KEY%(user_id)
        # 修改全品类优惠券
        if not course_id:
            payment_global_dict = json.loads(self.conn.hget(payment_global_key, 'coupon').decode('utf8'))
            if str(coupon_id) == '0':
                self.conn.hset(payment_global_key, 'default_coupon', 0)
            if coupon_id not in payment_global_dict:
                ret.error = '没有该优惠券'
                ret.code = 4002
                return Response(ret.__dict__)
            self.conn.hset(payment_global_key, 'default_coupon', coupon_id)
            ret.data = '全品类修改成功'
            return Response(ret.__dict__)
        coupon_dict = json.loads(self.conn.hget(payment_key, 'coupon').decode('utf8'))
        if str(coupon_id) == '0':
            self.conn.hset(payment_key, 'default_coupon', 0)
        if coupon_id not in coupon_dict:
            ret.error = '没有该优惠券'
            ret.code = 4002
            return Response(ret.__dict__)
        self.conn.hset(payment_global_key, 'default_coupon', coupon_id)
        ret.data = '全品类修改成功'

        return Response(ret.__dict__)

    def post(self, request, *args, **kwargs):
        """增加结算中心数据"""
        user_id = request.user.id
        # 每次添加先清空结算中心
        key_list = self.conn.keys(settings.PAYMENT_KEY%(user_id, '*'))
        key_list.append(settings.PAYGLOBAL_KEY%user_id)
        self.conn.delete(*key_list)
        ret = BaseResponse()
        # 获取要结算的课程id 列表
        course_ids = request.data.get('course_ids')
        payment_dict= {}
        for cid in course_ids:
            shopping_car_key = settings.SHOPPING_CAR_KEY%(user_id, cid)
            # 课程不在结算中心
            if not self.conn.exists(shopping_car_key):
                ret.code = 4001
                ret.error = '课程需要加入购物车后才能结算'
                return Response(ret.__dict__)
            policy = json.loads(str(self.conn.hget(shopping_car_key, 'policy'), encoding='utf8'))
            default_policy = str(self.conn.hget(shopping_car_key, 'default_policy'), encoding='utf8')
            policy_info = policy[default_policy]
            payment_info_dict = {
                "course_id": str(cid),
                "title": self.conn.hget(shopping_car_key, 'title').decode('utf-8'),
                "image": self.conn.hget(shopping_car_key, 'image').decode('utf-8'),
                "policy_id": default_policy,
                "coupon": {},
                "default_coupon": 0
            }
            # 使用update 就不需要每次进行循环了
            payment_info_dict.update(policy_info)
            payment_dict[cid] = payment_info_dict
        current_time = datetime.date.today()
        coupon_list = Coupon.objects.filter(valid_begin_date__lte=current_time, valid_end_date__gte = current_time,
                              couponrecord__status=0, couponrecord__account=request.user).all()
        coupon_global_dict = {'coupon':{}, "default_coupon":0}
        for coupon in coupon_list:
            course_id = coupon.object_id
            coupon_type = coupon.coupon_type
            # 未绑定课程，全品类优惠券
            if not coupon.object_id:
                info = {}
                if coupon_type == 0:  # 立减
                    info['money_equivalent_value'] = coupon.money_equivalent_value
                elif coupon_type == 1:  # 满减券
                    info['money_equivalent_value'] = coupon.money_equivalent_value
                    info['minimum_consume'] = coupon.minimum_consume
                else:  # 折扣
                    info['off_percent'] = coupon.off_percent
                info['coupon_type'] = coupon_type
                coupon_global_dict['coupon'][coupon.id] = info
                continue
            info = {}
            if coupon_type == 0:  # 立减
                info['money_equivalent_value'] = coupon.money_equivalent_value
            elif coupon_type == 1:  # 满减券
                info['money_equivalent_value'] = coupon.money_equivalent_value
                info['minimum_consume'] = coupon.minimum_consume
            else:  # 折扣
                info['off_percent'] = coupon.off_percent
            info['coupon_type'] = coupon_type

            # 有些优惠券不适合结算中心的商品
            if course_id not in payment_dict:
                continue
            payment_dict[course_id]['coupon'][coupon.id] = info

        # 存放到redis中
        for k,v in payment_dict.items():
            payment_key = settings.PAYMENT_KEY%(user_id, k)
            v['coupon'] = json.dumps(v['coupon'])
            self.conn.hmset(payment_key, v)
        # 字典第二层如果还是字典，就应该序列化后再存储。如若不然，那么取出来bytes经过decode之后变成str
        # 这时候想要得到字典是不行的，因为内部没有经过dumps,此时字符串内部的字符串是单引号"{'b': 1, 'c': 2}"
        # 这样是无法loads的，只有'{"b": 1, "c": 2}' 这样的格式才能loads
        coupon_global_dict['coupon'] = json.dumps(coupon_global_dict['coupon'])
        self.conn.hmset(settings.PAYGLOBAL_KEY%user_id, coupon_global_dict)
        ret.data = '添加到结算中心成功'
        return Response(ret.__dict__)
