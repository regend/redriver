# coding=utf-8
import unittest
import sys
from src.backOffice.boIndex import BoIndex
from src.backOffice.boRegister import BoRegister
from src.backOffice.boOrderView import BoOrderView
from src.backOffice.boOrderSave import BoOrderSave
from src.backOffice.boPlacement import BoPlacement
from src.backOffice.boSponsor import BoSponsor
from util import HTMLTestRunner
from util.initialize import Initialize


__author__ = 'Regend'


def run_suit():

    suit = unittest.TestSuite([
        load_case(BoIndex),
        # load_case(BoRegister),
        # load_case(BoOrderSave),
        load_case(BoOrderView),
        load_case(BoPlacement),
        load_case(BoSponsor)
    ])

    return suit


def load_case(name):
    return unittest.TestLoader().loadTestsFromTestCase(name)

if __name__ == "__main__":
    Initialize().set_build_number(sys.argv[1], True)
    reportFile = file(Initialize().datapath + sys.argv[1] + "\\backOffice_report.html", "wb")
    runner = HTMLTestRunner.HTMLTestRunner(stream=reportFile, title=u'测试结果', description=u'测试报告', version=sys.argv[1], env='production')
    runner.run(run_suit())