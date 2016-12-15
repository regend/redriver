# coding=utf-8
import unittest
from selenium.webdriver import ActionChains
from db.ora.oradao import Oradao
from util.datview import transData
from util.initialize import Initialize
from util.ranchar import ranNo
import time

__author__ = 'Maggie'


class OrderChange(unittest.TestCase):
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

    def testOrderChange(self):

        driver = self.driver
        conf = self.conf
        state = conf.state
        conf.stateChange(driver)
        driver.implicitly_wait(10)

        # OM003 换货单管理-查询
        # 选择运营支撑平台-销售管理
        driver.find_element_by_id('topMenu_1100').click()
        button = driver.find_element_by_id('left_menu_1120')
        menu = driver.find_element_by_class_name('nav-header')

        # 鼠标悬停在销售管理上
        chain = ActionChains(driver)
        chain.move_to_element(button).perform()
        driver.implicitly_wait(10)

        # 选择换货单管理
        driver.find_element_by_xpath('//li[@id="left_menu_28740"]/a/span').click()
        chain.move_to_element(menu).perform()

        driver.implicitly_wait(10)
        # 切换至iframe
        driver.switch_to_frame('contentIframe28740')

        # 从数据库随机取一个换货订单编号
        changeOrder = Oradao.sqlDiy(Oradao(), 'select co.doc_no as c_doc_no,o.doc_no,m.member_no,m.name,co.order_date,co.total_pv,co.total_bv,co.total_net_amount,co.order_status from om_change_orders co,mm_member m,om_orders o where m.id=co.member_id and co.om_orders_id=o.id and co.order_status!=30 and co.company_code=\''+state+'\'')
        num = ranNo(0, changeOrder['C_DOC_NO'].__len__()-1)
        c_doc_no = changeOrder['C_DOC_NO'][num]

        # 把随机取到的订单编号放到页面查询
        driver.find_element_by_name('sp_docNo_LIKE').send_keys(c_doc_no)
        driver.find_element_by_id('btnSubmit').click()
        time.sleep(2)

        # 按订单编号查询到的条数，判断是否1条
        rsNum = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr').__len__()-1
        self.assertEquals(rsNum, 1)

        # 获取列表各字段数据
        rsXpath = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td')

        rsDocNo = rsXpath[0].text
        rsOrderDate = rsXpath[1].text
        rsOrderMember = rsXpath[2].text
        rsOrderPV = rsXpath[3].text
        rsOrderBV = rsXpath[4].text
        rsOrderPrice = rsXpath[5].text
        rsOrderStatus = rsXpath[6].text

        # 断言
        self.assertEquals(rsDocNo, changeOrder['C_DOC_NO'][num]+' / ' + changeOrder['DOC_NO'][num])
        self.assertEqual(rsOrderDate, changeOrder['ORDER_DATE'][num].strftime('%Y-%m-%d %H:%M:%S'))
        self.assertEqual(rsOrderMember, changeOrder['MEMBER_NO'][num]+' / ' + changeOrder['NAME'][num])
        self.assertEqual(rsOrderPV.replace(',', ''), "%.2f" % float(changeOrder['TOTAL_PV'][num]))
        self.assertEqual(rsOrderBV.replace(',', ''), "%.2f" % float(changeOrder['TOTAL_BV'][num]))
        self.assertEqual(rsOrderPrice.replace(',', ''), "%.2f" % float(changeOrder['TOTAL_NET_AMOUNT'][num]))
        if changeOrder['ORDER_STATUS'][num] != '10':
            self.assertEqual(rsOrderStatus, transData('order.orderStatus').get(changeOrder['ORDER_STATUS'][num]))

if __name__ == '__main__':
    unittest.main()