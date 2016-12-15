# coding=utf-8

import unittest
import time
from db.ora.oradao import Oradao
from util.boInitialize import BoInitialize
from util.datview import transData
from util.ranchar import ranNo

__author__ = 'Maggie'


class BoOrderView(unittest.TestCase):
    def setUp(self):
        self.conf = BoInitialize()
        self.driver = self.conf.login()
        self.verificationErrors = []
        pass

    def tearDown(self):
        self.conf.getScreenshot(self)
        self.assertEqual([], self.verificationErrors)
        self.driver.quit()
        pass

    # bo005 下单查询
    def testBoOrderView(self):
        driver = self.driver
        conf = self.conf
        # 切换语言
        conf.boLangChange(driver, 'zh_CN')
        # 声明member对象
        member = conf.member
        member_id = member['ID']
        time.sleep(2)

        # 打开订单-我的订单
        driver.find_element_by_xpath('//ul[@id="mainmenu"]/li[4]/a').click()
        driver.find_element_by_id('28718').click()
        time.sleep(2)

        # 数据库取订单号
        order = Oradao.sqlDiy(Oradao(), 'select * from om_orders o where o.member_id =\''+str(member_id)+'\'order by o.doc_no desc')
        try:
            num = ranNo(0, order['ID'].__len__() - 1)
            doc_no = order['DOC_NO'][num]

            # 查询
            driver.find_element_by_name('sp_docNo_LIKE').send_keys(doc_no)
            driver.find_element_by_id('btnSubmit').click()
            time.sleep(2)

            # 获取页面订单各字段数据
            rs_xpath = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr/td')
            rs_doc_no = rs_xpath[0].text
            rs_bonus_date = rs_xpath[1].text
            rs_total_pv = rs_xpath[2].text
            rs_total_bv = rs_xpath[3].text
            rs_total_amount = rs_xpath[4].text
            rs_order_type = rs_xpath[5].text
            rs_order_status = rs_xpath[6].text

            # 断言
            self.assertEqual(rs_doc_no, doc_no)
            if rs_bonus_date == '':
                self.assertEqual(rs_bonus_date, order['BONUS_DATE'][num])
            else:
                self.assertEqual(rs_bonus_date, order['BONUS_DATE'][num].strftime('%Y-%m-%d %H:%M:%S'))
            self.assertEqual(rs_total_pv.replace(',', ''), "%.2f" % float(order['TOTAL_PV'][num]))
            self.assertEqual(rs_total_bv.replace(',', ''), "%.2f" % float(order['TOTAL_BV'][num]))
            self.assertEqual(rs_total_amount.replace(',', ''), "%.2f" % float(order['TOTAL_NET_AMOUNT'][num]))
            self.assertEqual(rs_order_type, transData('order.orderType').get(order['ORDER_TYPE'][num]))
            self.assertEqual(rs_order_status, transData('order.orderStatus').get(order['ORDER_STATUS'][num]))
        except:
            print(u'结束查询')

if __name__ == '__main__':
    unittest.main()