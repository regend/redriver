# coding=utf-8
import unittest
import sys
from src.router.router import Router
from util import HTMLTestRunner
from util.initialize import Initialize


__author__ = 'Maggie'


def run_suit():

    suit = unittest.TestSuite([
        load_case(Router)
    ])

    return suit


def load_case(name):
    return unittest.TestLoader().loadTestsFromTestCase(name)

if __name__ == "__main__":
    Initialize().set_build_number(sys.argv[1], True)
    reportFile = file(Initialize().datapath + sys.argv[1] + "\\router_report.html", "wb")
    runner = HTMLTestRunner.HTMLTestRunner(stream=reportFile, title=u'测试结果', description=u'测试报告', version=sys.argv[1])
    runner.run(run_suit())