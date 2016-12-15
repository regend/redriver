# coding=utf-8
import unittest
from selenium.webdriver import ActionChains
from db.ora.oradao import Oradao
from util.datview import transData
from util.initialize import Initialize
from util.ranchar import ranNo
import time

__author__ = 'Maggie'


class OrderReturn(unittest.TestCase):
    def setUp(self):
        # 初始化登录
        self.conf = Initialize()
        self.driver = self.conf.start()
        self.verificationErrors = []
        pass

    def tearDown(self):
        self.conf.getScreenshot(self)
        self.assertEqual([], self.verificationErrors)
        self.driver.quit()
        pass

    def testOrderReturn(self):

        driver = self.driver
        conf = self.conf
        state = conf.state
        conf.stateChange(driver)
        driver.implicitly_wait(10)

        # OM005 退货单管理-查询
        # 选择运营支撑平台-销售管理
        driver.find_element_by_id('topMenu_1100').click()
        button = driver.find_element_by_id('left_menu_1120')
        menu = driver.find_element_by_class_name('nav-header')

        # 鼠标悬停在销售管理上
        chain = ActionChains(driver)
        chain.move_to_element(button).perform()
        driver.implicitly_wait(10)

        # 选择退货单管理
        driver.find_element_by_xpath('//li[@id="left_menu_2604"]/a/span').click()
        chain.move_to_element(menu).perform()

        driver.implicitly_wait(10)

        # 切换至iframe
        driver.switch_to_frame('contentIframe2604')

        # 从数据库随机取一个退货订单编号
        returnOrder = Oradao.sqlDiy(Oradao(), 'select r.id,r.return_order_no,m.member_no,r.total_amount,r.actual_refund,r.total_bv,r.total_pv,o.doc_no,o.order_type,r.check_statu from om_return_order r,om_orders o,mm_member m where r.order_id=o.id and r.member_id=m.id and o.company_code=\''+state+'\'')
        num = ranNo(0, returnOrder['ID'].__len__()-1)
        r_order_no = returnOrder['RETURN_ORDER_NO'][num]

        # 把随机取到的订单编号放到页面查询
        driver.find_element_by_name('sp_returnOrderNo_LIKE').send_keys(r_order_no)
        driver.find_element_by_id('btnSubmit').click()
        time.sleep(2)

        # 按订单编号查询到的条数，判断是否1条
        rsNum = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr').__len__()-1
        self.assertEquals(rsNum, 1)

        # 获取列表各字段数据
        rsXpath = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td')

        rsReturnNo = rsXpath[0].text
        rsMember = rsXpath[1].text
        rsTotalAmount = rsXpath[2].text
        rsActualRefund = rsXpath[3].text
        rsBV = rsXpath[4].text
        rsPV = rsXpath[5].text
        rsDocNo = rsXpath[6].text
        rsOrderType = rsXpath[7].text
        rsReturnStatus = rsXpath[8].text

        # 断言
        self.assertEquals(rsReturnNo, returnOrder['RETURN_ORDER_NO'][num])
        self.assertEqual(rsMember, returnOrder['MEMBER_NO'][num])
        self.assertEqual(rsTotalAmount.replace(',', ''), "%.2f" % float(returnOrder['TOTAL_AMOUNT'][num]))
        self.assertEqual(rsActualRefund.replace(',', ''), "%.2f" % float(returnOrder['ACTUAL_REFUND'][num]))
        self.assertEqual(rsBV.replace(',', ''), "%.2f" % float(returnOrder['TOTAL_BV'][num]))
        self.assertEqual(rsPV.replace(',', ''), "%.2f" % float(returnOrder['TOTAL_PV'][num]))
        self.assertEqual(rsDocNo, returnOrder['DOC_NO'][num])
        self.assertEqual(rsOrderType, transData('order.orderType').get(returnOrder['ORDER_TYPE'][num]))
        if returnOrder['CHECK_STATU'][num] != '21':
            self.assertEqual(rsReturnStatus, transData('returnOrder.checkStatus').get(str(returnOrder['CHECK_STATU'][num])))

if __name__ == '__main__':
    unittest.main()