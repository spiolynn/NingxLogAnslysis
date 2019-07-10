# -*- coding: utf-8 -*-
# @Time    : 2019/7/10 15:31
# @Author  : hoo
# @Site    : 
# @File    : NingxLog.py
# @Software: PyCharm Community Edition


import argparse
import os
import fnmatch
import datetime
import traceback
import PatternStrategy
import NginxLogStatistical

'''
nginx 日志分析
'''

class NginxLog:

    def __init__(self,logpath):
        self._logpath = logpath
        self.nginx_log_list = []

    def GetLogFileList(self,matchRuleList):
        '''
        根据 matchRuleList 匹配日志文件信息 进行pattern
        :param matchRuleList: 日志匹配规则
        :return: 文件清单
        '''
        for root, dirs, files in os.walk(self._logpath):
            for name in files:
                if os.path.isfile(os.path.join(root, name)):
                    for rule_i in matchRuleList:
                        if not fnmatch.fnmatch(name, rule_i):
                            continue
                        else:
                            abspath = os.path.join(root,name)
                            self.nginx_log_list.append(os.path.join(root,name))


# 入参接收
def ParseArgs():
    parser = argparse.ArgumentParser(description='set input arguments')
    parser.add_argument("-p", "--path", dest="analysis_path", type=str, metavar='<str>', required=False,
                        help="The path to the nginx directory",default="./nginx_logs")
    parser.add_argument("-t", "--time", dest="analysis_timedelta", type=int, metavar='<int>', required=False,
                        help="analysis time delta, default= 60min",default=9999)
    parser.add_argument("-l", "--trade", dest="analysis_tradelist", type=str, metavar='<str>', required=False,
                        help="analysis tradeList",default='./nginx_logs/trade_mode.txt')
    args = parser.parse_args()

    print('*'*50)
    print("analysis_path: " + args.analysis_path)
    print("analysis_timedelta: " + str(args.analysis_timedelta))
    print("analysis_tradelist: " + args.analysis_tradelist)
    print('*'*50)

    return args


# 批量分析nginx日志
def AnalysisNginxLog(nginx_log_list,timedelta,PatternStrategy):
    '''
    批量日志分析
    :param nginx_log_list:    ['log.1','log.2'] 日志列表
    :param timedelta:         时间间隔
    :param PatternStrategy:   匹配策略
    :return: no
    '''

    # logfile = PatternStrategy.name + '_' +(datetime.datetime.now()).strftime('%Y%m%d') + ".log"
    try:
        # logfilef = open(PatternStrategy., 'w', encoding='utf-8')
        # logfilef.close()
        for _nginx_log in nginx_log_list:
            print("{}-{}".format("begin analysis - ",_nginx_log))
            ReWriteNginxLogfile(_nginx_log,timedelta,PatternStrategy)
    except:
        pass


# 单个nginx日志分析
def ReWriteNginxLogfile(nginx_logfile,timedelta,PatternStrategy):
    '''
    分析日志交易的占比
    :param nginx_logfile:  日志绝对路径
    :param _timedelta: 时间时间间隔 min
    :return:
    '''

    # 设置title
    title = PatternStrategy.title
    logfilef = PatternStrategy.logfilef
    logfilef.write(str(title) + "\n")
    nginx_err_pattern_line = 0

    if not os.path.isfile(nginx_logfile):
        print('{}-{}',nginx_logfile," is not nginxLogFile")
        return 1

    try:
        # 文件数据异常处理
        with open(nginx_logfile, "rb") as f:
            lines = f.readlines()
            for line_i,line in enumerate(lines):
                try:
                    line_decode = line.decode(encoding='utf-8')
                except UnicodeDecodeError:
                    print("filewarning-{}-{}".format(str(line_i),str(line)[:200]))
                    continue

                # everyline analysis
                line_new = PatternStrategy.PatternLine(line_decode,timedelta)

                if line_new:
                    logfilef.write(str(line_new) + "\n")
                else:
                    # 异常日志忽略
                    nginx_err_pattern_line = nginx_err_pattern_line + 1

        print("nginx_err_pattern_line: " + str(nginx_err_pattern_line))
        logfilef.close()
    except:
        logfilef.close()
        traceback.print_exc()


def main_VerboseTime_log():
    args = ParseArgs()
    a_nginxlog = NginxLog(args.analysis_path)
    rule = ["access_443_time*.log"]
    a_nginxlog.GetLogFileList(rule)
    print("nginx loglist: " + str(a_nginxlog.nginx_log_list))

    # 日志解析
    StrategyVerboseTime = PatternStrategy.PatternStrategyVerboseTime()
    AnalysisNginxLog(a_nginxlog.nginx_log_list, args.analysis_timedelta, StrategyVerboseTime)

    #  日志分析可视化
    file = StrategyVerboseTime.logfile
    trademodefile = args.analysis_tradelist
    NginxLogStatistical.LogStatis(file,trademodefile)


def main():
    main_VerboseTime_log()



def havafun():
    from pycallgraph import PyCallGraph
    from pycallgraph.output import GraphvizOutput
    graphviz = GraphvizOutput()
    graphviz.output_file = 'basic.png'
    with PyCallGraph(output=graphviz):
        main_VerboseTime_log()



if __name__ == '__main__':
    havafun()