# -*- coding: utf-8 -*-
# @Time    : 2019/7/10 17:04
# @Author  : hoo
# @Site    : 
# @File    : havefun.py
# @Software: PyCharm Community Edition


'''
好玩的事情
'''




from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
import NingxLog

if __name__ == '__main__':

    graphviz = GraphvizOutput()
    graphviz.output_file = 'basic.png'

    with PyCallGraph(output=graphviz):
        NingxLog.main()
