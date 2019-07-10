# -*- coding: utf-8 -*-
# @Time    : 2019/7/10 15:11
# @Author  : hoo
# @Site    : 
# @File    : pub_test.py
# @Software: PyCharm Community Edition

'''
pub 单元测试
'''

import unittest

import pub
import datetime

class TestDict(unittest.TestCase):
    def test_init(self):
        pass

    def test_GetTime(self):
        r_time_local = "[10/Jul/2019:10:19:14 +0800]"
        _timedelta = 60
        r_time_local_time = datetime.datetime.strptime(r_time_local, '[%d/%b/%Y:%H:%M:%S +0800]')

        result = pub.GetTime(r_time_local_time, _timedelta)
        self.assertEquals(result, False)