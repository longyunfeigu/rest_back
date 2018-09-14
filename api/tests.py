from django.test import TestCase

# Create your tests here.
from redis import Redis
import json

conn = Redis('10.20.1.18', port='6379', password='123456')

dic = {'name':'jack', 'age': {"b":1, "c":2}}
conn.hmset('a', dic)
# res = conn.hgetall('a')
# print(res)
r1 = conn.hget('a', 'age')
print(r1)
print(json.loads(r1.decode('utf8')))