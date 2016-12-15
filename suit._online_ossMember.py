# coding=utf-8
import unittest
import sys
from src.ossMember.member.member import MemberInfo
from src.ossMember.member.memberAdd import MemberAdd
from src.ossMember.member.placementSelect import PlacementSelect
from src.ossMember.orders.order_Change import OrderChange
from src.ossMember.orders.order_Change_Add import OrderChangeAdd
from src.ossMember.orders.order_Return import OrderReturn
from src.ossMember.orders.order_Return_Check import OrderReturnCheck
from src.ossMember.orders.order_Save import OrderSave
from src.ossMember.orders.order_View import OrderView
from src.ossMember.product.productComposite import ProductComposite
from src.ossMember.product.productMsg_new import ProductNewMSG
from src.ossMember.product.productMsg_search import ProductMsgSearch
from src.ossMember.product.productSaleTax import ProductSaleTax
from src.ossMember.product.product_No import ProductNo
from src.ossMember.product.product_Search import ProductSearch
from util import HTMLTestRunner
from util.initialize import Initialize


__author__ = 'Regend'


def run_suit():

    suit = unittest.TestSuite([
        # load_case(ProductNo),
        load_case(ProductSearch),
        # load_case(ProductComposite),
        # load_case(ProductNewMSG),
        load_case(ProductMsgSearch),
        load_case(ProductSaleTax),
        load_case(MemberInfo),
        # load_case(MemberAdd),
        load_case(PlacementSelect),
        load_case(OrderChange),
        # load_case(OrderChangeAdd),
        load_case(OrderReturn),
        # load_case(OrderReturnCheck),
        load_case(OrderView),
        load_case(OrderSave)
    ])

    return suit


def load_case(name):
    return unittest.TestLoader().loadTestsFromTestCase(name)

if __name__ == "__main__":
    Initialize().set_build_number(sys.argv[1], True)
    reportFile = file(Initialize().datapath + sys.argv[1] + "\\ossMember_report.html", "wb")
    runner = HTMLTestRunner.HTMLTestRunner(stream=reportFile, title=u'测试结果', description=u'测试报告', version=sys.argv[1], env='production')
    runner.run(run_suit())