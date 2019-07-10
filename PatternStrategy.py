# -*- coding: utf-8 -*-
# @Time    : 2019/7/10 14:54
# @Author  : hoo
# @Site    : 
# @File    : PatternStrategy.py
# @Software: PyCharm Community Edition

import re
import datetime
import fnmatch
import pub
import hashlib

'''
nginx 日志匹配策略
'''

class PatternStrategySuper(object):
    '''
    匹配超类
    '''

    def __init__(self):

        self.name = "PatternStrategySuper"
        self.title = ""
        self.field_remote_addr = r"?P<l_remote_addr>.*"
        # field 1
        self.field_remote_user = r"?P<l_remote_user>-.*"
        # field 2
        self.field_time_local = r"?P<l_time_local>\[.*\]"
        # field 3
        self.field_request = r"?P<l_request>\"[^\"]*\""
        # field 4
        self.field_status = r"?P<l_status>.*"
        # field 5
        self.field_body_bytes_sent = r"?P<l_body_bytes_sent>\d+"
        # field 6
        self.field_http_refere = r"?P<l_http_refere>\"[^\"]*\""
        # field 7
        self.field_http_user_agent = r"?P<l_http_user_agent>\"[^\"]*\""
        # field 8
        self.field_http_x_fowarded_for = r"?P<l_http_x_fowarded_for>\"[^\"]*\""
        # field 9
        self.field_request_body = r"?P<l_request_body>\"[^\"]*\""
        # field 10
        # self.field_request_time = r"?P<l_request_time>^(-?\d+)(\.\d+)?$"
        self.field_request_time = r"""?P<l_request_time>
                    [^\"]*
                   """
        # field 10
        self.field_upstream_response_time =  r"""?P<l_upstream_response_time>
                    [^\"]*
                   """

    def PatternLine(self,line,delta):
        raise NotImplementedError()

    def ParseLineList(self):
        raise NotImplementedError()




class PatternStrategyMain(PatternStrategySuper):

    '''
    匹配: verbose_time
    log_format  main escape=json  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';
    '''

    def __init__(self):
        super(PatternStrategyMain,self).__init__()
        self.name = "PatternStrategyMain"
        self.title = '{}@{}@{}@{}@{}@{}@{}@{}@{}'.format("field_remote_addr","field_remote_user","field_time_local","field_request", \
                                             "field_status","field_body_bytes_sent","field_http_refere","field_http_user_agent","field_http_x_fowarded_for")

        self.nginx_time_pattern = re.compile(r"(%s)\s(%s)\s(%s)\s(%s)\s(%s)\s(%s)\s(%s)\s(%s)\s(%s)" \
                                      % (self.field_remote_addr, self.field_remote_user, self.field_time_local, self.field_request, self.field_status, \
                                         self.field_body_bytes_sent ,self.field_http_refere,self.field_http_user_agent,self.field_http_x_fowarded_for \
                                         ), re.VERBOSE)

        self.logfile = self.name + '_' +(datetime.datetime.now()).strftime('%Y%m%d') + ".log"
        self.logfilef = open(self.logfile, 'w', encoding='utf-8')


    def __del__(self):
        self.logfilef.close()

    # 匹配verbose_time日志行
    def PatternLine(self, line, delta):

        '''
        匹配verbose_time日志行
        :param line:  log line string
        :param delta:  time delta
        :return: line
        '''
        _line_regular = self.nginx_time_pattern.match(line)
        if _line_regular != None:
            try:
                allgroup = _line_regular.groups()
                r_remote_addr = allgroup[0]
                r_remote_user = allgroup[1]
                r_time_local = allgroup[2]
                r_time_local_time = datetime.datetime.strptime(r_time_local, '[%d/%b/%Y:%H:%M:%S +0800]')
                if not pub.GetTime(r_time_local_time,delta):
                    print(str(r_time_local_time) + " - delta is pass")
                    return None

                # request handle
                r_request = allgroup[3]
                r_request_method = r_request.replace('"', '').split(' ')[0]
                r_request_url = r_request.replace('"', '').split(' ')[1]
                # url 聚合
                r_request_url_real = r_request_url.split('?')[0]
                # 特殊url 跳过
                if fnmatch.fnmatch(r_request_url_real, "*\\x00*"):
                    print(str(r_request_url_real) + " - is pass")
                    return None

                r_stutas = allgroup[4]
                r_body_bytes_sent = allgroup[5]
                r_http_refere = allgroup[6]
                r_field_http_user_agent = allgroup[7]
                r_http_x_fowarded_for = allgroup[8]


                #  r_trade_key_str md5 主键
                r_trade_key = hashlib.md5()
                r_trade_key.update("{}{}".format(r_request_method, r_request_url_real).encode())
                r_trade_key_str = r_trade_key.hexdigest()

                # 特殊url 处理
                is_special_url,special_url = Special_url(r_request_url_real,r_request_method)

                if is_special_url:
                    # 特殊url 汇聚
                    r_trade_key_str = is_special_url # update md5
                    r_request_url_real = special_url # update url

                line_new = '{}@{}@{}@{}@{}@{}'.format(r_remote_addr,r_time_local_time,r_stutas, \
                                                            r_request_method,r_request_url_real,r_trade_key_str)
                return line_new
            except:
                print("warning - prase fail{}".format(str(line)[:200]))
                return None
        else:
            print("pattern is fail")
            return None


class PatternStrategyVerboseTime(PatternStrategySuper):

    '''
    匹配: verbose_time
    log_format  verbose_time '$remote_addr [$time_local] '
                      '$status '
                      '$request_time '
                      '$upstream_response_time '
                      '"$request" $body_bytes_sent ';
    '''

    def __init__(self):
        super(PatternStrategyVerboseTime,self).__init__()
        self.name = "PatternStrategyVerboseTime"
        self.title = '{}@{}@{}@{}@{}@{}@{}@{}'.format("r_remote_addr","r_time_local_time","r_stutas","r_request_time", \
                                             "r_upstream_response_time","r_request_method","r_request_url_real","r_trade_key_str")

        self.nginx_time_pattern = re.compile(r"(%s)\s(%s)\s(%s)\s(%s)\s(%s)\s(%s)\s(%s)" \
                                      % (self.field_remote_addr, self.field_time_local, self.field_status, \
                                         self.field_request_time, self.field_upstream_response_time,self.field_request, self.field_body_bytes_sent \
                                         ), re.VERBOSE)

        self.logfile = self.name + '_' +(datetime.datetime.now()).strftime('%Y%m%d') + ".log"
        self.logfilef = open(self.logfile, 'w', encoding='utf-8')


    def __del__(self):
        self.logfilef.close()

    # 匹配verbose_time日志行
    def PatternLine(self, line, delta):

        '''
        匹配verbose_time日志行
        :param line:  log line string
        :param delta:  time delta
        :return: line
        '''

        _line_regular = self.nginx_time_pattern.match(line)
        if _line_regular != None:
            try:
                allgroup = _line_regular.groups()
                r_remote_addr = allgroup[0]
                r_time_local = allgroup[1]
                r_time_local_time = datetime.datetime.strptime(r_time_local, '[%d/%b/%Y:%H:%M:%S +0800]')

                if not pub.GetTime(r_time_local_time,delta):
                    print(str(r_time_local_time) + " - delta is pass")
                    return None

                r_stutas = allgroup[2]
                r_request_time = allgroup[3]
                r_upstream_response_time = allgroup[4]

                # 存在nginx log中upstream_response_time为空的情况
                if r_upstream_response_time == "-":
                    r_upstream_response_time = "0.00"


                r_request = allgroup[5]
                r_request_method = r_request.replace('"', '').split(' ')[0]
                r_request_url = r_request.replace('"', '').split(' ')[1]

                # url 聚合
                r_request_url_real = r_request_url.split('?')[0]

                # 特殊url 跳过
                if fnmatch.fnmatch(r_request_url_real, "*\\x00*"):
                    print(str(r_request_url_real) + " - is pass")
                    return None

                r_body_bytes_sent = allgroup[6]

                #  r_trade_key_str md5 主键
                r_trade_key = hashlib.md5()
                r_trade_key.update("{}{}".format(r_request_method, r_request_url_real).encode())
                r_trade_key_str = r_trade_key.hexdigest()

                # 特殊url 处理
                is_special_url,special_url = Special_url(r_request_url_real,r_request_method)

                if is_special_url:
                    # 特殊url 汇聚
                    r_trade_key_str = is_special_url # update md5
                    r_request_url_real = special_url # update url

                line_new = '{}@{}@{}@{}@{}@{}@{}@{}'.format(r_remote_addr,r_time_local_time,r_stutas,r_request_time, \
                                                            r_upstream_response_time,r_request_method,r_request_url_real,r_trade_key_str)
                return line_new

            except:
                print("warning - prase fail{}".format(str(line)[:200]))
                return None
        else:
            print("pattern is fail")
            return None


def Special_url(url, method):
    '''
    自定义url 汇聚
    :param url:     url
    :param method:  post get..
    :return:  [md5,new_url] or [None None]
    '''
    special_dicts = {
                     "/vet_vcss_ics/api/personInfo/getDetail/*": "0000000000000000000000000000001",
                     "/vet_vcss_ics/api/meetInfoFill/mod/*": "0000000000000000000000000000002",
                     "/vet_vcss_ics/api/meetInfo/delete/*": "0000000000000000000000000000003",
                     "/vet_vcss_iu/api/vet/delusrinfo/*": "0000000000000000000000000000004",
                     "/vet_vcss_plcy/api/gm/plcy/searchDetails/*": "0000000000000000000000000000005",
                     "/vet_vcss_iu/api/queryuserdetail/*": "0000000000000000000000000000006",
                     "/_nuxt/*": "0000000000000000000000000000007",
                     "/images/*": "0000000000000000000000000000008",
                     "/icon/*": "0000000000000000000000000000009",
                     "/infoDetail-*index.html":"0000000000000000000000000000010"
                     }

    for pattern_k, patter_v in special_dicts.items():
        if fnmatch.fnmatch(url, pattern_k):
            if method == 'GET':
                return ["0" + patter_v, pattern_k]
            elif method == 'POST':
                return ["1" + patter_v, pattern_k]
            elif method == "PUT":
                return ["2" + patter_v, pattern_k]
            elif method == "DELETE":
                return ["3" + patter_v, pattern_k]
            else:
                return ["9" + patter_v, pattern_k]
    return [None, None]




def _test_PatternStrategyMain():

    a_StrategyMain = PatternStrategyMain()
    line = '171.10.177.255 -  [10/Jul/2019:18:18:36 +0800] "GET /fetchuserinfo HTTP/1.1" 200 22939 "https://servicewechat.com/wxa290933507eb6b7b/17/page-frame.html" "Mozilla/5.0 (Linux; Android 8.1.0; vivo X9s Plus Build/OPM1.171019.019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/62.0.3202.84 Mobile Safari/537.36 MicroMessenger/7.0.4.1420(0x2700043C) Process/appbrand0 NetType/4G Language/zh_CN" ""'
    print(a_StrategyMain.PatternLine(line,999999))


if __name__ == '__main__':
    _test_PatternStrategyMain()
