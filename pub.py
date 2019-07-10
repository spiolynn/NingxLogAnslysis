# -*- coding: utf-8 -*-
# @Time    : 2019/7/10 15:06
# @Author  : hoo
# @Site    : 
# @File    : pub.py
# @Software: PyCharm Community Edition


'''
公共方法
'''

import datetime
import pickle

def GetTime(r_time_local_time, _timedelta):
    '''
    时间比较
    :param r_time_local_time:
    :param _timedelta:
    :return:
    '''
    now_time = datetime.datetime.now()
    minutes = (now_time - r_time_local_time)
    _time_ = datetime.timedelta(seconds=_timedelta * 60)
    if minutes > _time_:
        return False
    else:
        return True


def saveTradeObject(_object, _saveobjectNm):
    '''
    保存对象
    :return:
    '''
    f = open(_saveobjectNm, 'wb')
    pickle.dump(_object, f)

def loadTradeObject(_saveobjectNm):
    f = open(_saveobjectNm, 'rb')
    _object = pickle.load(f)
    return _object