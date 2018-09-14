#!/usr/bin/env python
# -*- coding:utf-8 -*-

class BaseResponse(object):
    def __init__(self):
        self.code = 1000
        self.data = None
        self.error = None