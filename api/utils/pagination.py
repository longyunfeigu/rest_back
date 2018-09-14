#!/usr/bin/env python
# -*- coding:utf-8 -*-
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from collections import OrderedDict

class Pagination:
    def get_paginated_response(self, data):
        return OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ])

class MyLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 1
    def get_paginated_response(self, data):
        return OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ])


class MyPageNumberPagination(Pagination, PageNumberPagination):
    page_size = 1
    page_query_param = 'page'
    page_size_query_param = 'size'
    max_page_size = 2