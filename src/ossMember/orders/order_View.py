# coding=utf-8
import unittest
from selenium.webdriver import ActionChains
from db.ora.oradao import Oradao
from util.datview import transData
from util.initialize import Initialize
from util.ranchar import ranNo
import time

__author__ = 'Maggie'


class OrderView(unittest.TestCase):
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

    def testOrderView(self):
        driver = self.driver
        conf = self.conf
        conf.stateChange(driver)
        driver.implicitly_wait(10)

        # OM001 订单查询
        # 选择运营支撑平台
        driver.find_element_by_id('topMenu_1100').click()
        button = driver.find_element_by_id('left_menu_1120')
        menu = driver.find_element_by_class_name('nav-header')

        # 鼠标悬停在销售管理上
        chain = ActionChains(driver)
        chain.move_to_element(button).perform()
        driver.implicitly_wait(10)
        driver.find_element_by_xpath('//li[@id="left_menu_1121"]/a/span').click()
        chain.move_to_element(menu).perform()

        driver.implicitly_wait(10)
        # 切换至iframe
        driver.switch_to_frame('contentIframe1121')

        # 从数据库随机取一个订单编号
        order = Oradao.sqlDiy(Oradao(),
                              'select * from om_orders o,mm_member m  where m.id=o.member_id and o.company_code=\'' + conf.state + '\'and o.doc_no like \'M%\'')
        num = ranNo(0, order['DOC_NO'].__len__() - 1)
        doc_no = order['DOC_NO'][num]

        # 把随机取到的订单编号放到页面查询
        if not driver.find_element_by_id('btnSubmit').is_displayed():
            driver.find_element_by_class_name('open-close').click()
        time.sleep(0.5)
        driver.find_element_by_name('sp_docNo_LIKE').send_keys(doc_no)
        driver.find_element_by_id('btnSubmit').click()
        time.sleep(2)

        # 按订单编号查询到的条数，判断是否1条
        rsNum = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr').__len__() - 1
        self.assertEquals(rsNum, 1)

        # 获取列表各字段数据
        rsXpath = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr[' + str(rsNum) + ']/td')

        if conf.env == 'production':
            rsDocNo = rsXpath[1].text
            rsOrderType = rsXpath[3].text
            rsOrderDate = rsXpath[5].text
            rsOrderBonus = rsXpath[6].text
            rsOrderMember = rsXpath[7].text
            rsOrderPV = rsXpath[9].text
            rsOrderBV = rsXpath[10].text
            rsOrderPrice = rsXpath[11].text
            rsOrderStatus = rsXpath[12].text
        else:
            rsDocNo = rsXpath[1].text
            rsOrderType = rsXpath[2].text
            rsOrderDate = rsXpath[4].text
            rsOrderBonus = rsXpath[5].text
            rsOrderMember = rsXpath[6].text
            rsOrderPV = rsXpath[8].text
            rsOrderBV = rsXpath[9].text
            rsOrderPrice = rsXpath[10].text
            rsOrderStatus = rsXpath[11].text

        # 断言
        self.assertEquals(rsDocNo, doc_no)
        self.assertEqual(rsOrderType, transData('order.orderType').get(order['ORDER_TYPE'][num]))
        self.assertEqual(rsOrderDate, order['ORDER_DATE'][num].strftime('%Y-%m-%d %H:%M:%S'))
        if rsOrderBonus == '':
            self.assertEqual(rsOrderBonus, order['BONUS_DATE'][num])
        else:
            self.assertEqual(rsOrderBonus, order['BONUS_DATE'][num].strftime('%Y-%m-%d'))
        self.assertEqual(rsOrderMember, order['MEMBER_NO'][num] + ' / ' + order['NAME'][num])
        self.assertEqual(rsOrderPV.replace(',', ''), "%.2f" % float(order['TOTAL_PV'][num]))
        self.assertEqual(rsOrderBV.replace(',', ''), "%.2f" % float(order['TOTAL_BV'][num]))
        self.assertEqual(rsOrderPrice.replace(',', ''), "%.2f" % float(order['TOTAL_NET_AMOUNT'][num]))
        if order['ORDER_STATUS'][num] != '10':
            self.assertEqual(rsOrderStatus, transData('order.orderStatus').get(order['ORDER_STATUS'][num]))


if __name__ == '__main__':
    unittest.main()
