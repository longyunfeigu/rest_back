#!/usr/bin/env python
# -*- coding:utf-8 -*-
from rest_framework.views import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin

from api.utils.response import BaseResponse
from api.utils.serializer import *
from api.models import *
from api.utils.pagination import MyPageNumberPagination
from api.utils.auth import MyAuthentication

class CourseView(ViewSetMixin, APIView):
    authentication_classes = []
    def list(self, request, *args, **kwargs):
        ret = BaseResponse()
        try:
            courses = Course.objects.all()
            paginator = MyPageNumberPagination()
            pager_courses = paginator.paginate_queryset(courses, request, view=self)
            ser = CourseSerializer(instance=pager_courses, many=True)
            response = paginator.get_paginated_response(ser.data)
            ret.data = response
        except Exception as e:
            ret.error = '未获取到资源'
            ret.code = 1001
        return Response(ret.__dict__)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        ret = BaseResponse()
        try:
            course_obj = Course.objects.get(pk=pk).coursedetail
            ser = SingleCourseSerializer(instance=course_obj, many=False)
            ret.data = ser.data
        except Exception as e:
            ret.error = '未获取到资源'
            ret.code = 1001
        return Response(ret.__dict__)

