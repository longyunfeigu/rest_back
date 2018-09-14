#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json

def regular(redis_value):
    """对redis字典数据进行规整"""
    return dict(map(lambda x: (str(x, encoding='utf-8'), json.loads(str(redis_value[x], encoding='utf8'))
    if x == b'policy' else str(redis_value[x], encoding='utf8')), redis_value))