# coding=utf-8
import unittest
from selenium.webdriver import ActionChains
import time
from db.ora.oradao import Oradao
from util.initialize import Initialize
from util.ranchar import ranNo

__author__ = 'Maggie'

class OrderReturnCheck(unittest.TestCase):
    def setUp(self):
        self.conf = Initialize()
        self.driver = self.conf.start()
        self.verificationErrors = []
        pass

    def tearDown(self):
        self.conf.getScreenshot(self)
        self.assertEqual([], self.verificationErrors)
        self.driver.quit()
        pass

    def testOrderReturnCheck(self):
        driver = self.driver
        conf = self.conf
        state = conf.state
        conf.stateChange(driver)
        driver.implicitly_wait(10)

        # OM006 退货单管理-审核
        # 先构造一条交易完成的订单数据(待发货--》交易完成)
        driver.find_element_by_id('topMenu_1100').click()
        button = driver.find_element_by_id('left_menu_1120')
        menu = driver.find_element_by_class_name('nav-header')

        chain = ActionChains(driver)
        chain.move_to_element(button).perform()
        driver.implicitly_wait(10)

        driver.find_element_by_xpath('//li[@id="left_menu_1121"]/a/span').click()
        chain.move_to_element(menu).perform()
        driver.implicitly_wait(10)
        driver.switch_to_frame('contentIframe1121')

        orderNo = Oradao.sqlDiy(Oradao(),
                                'select * from om_orders o where o.company_code=\''+state+'\'and o.order_status=20 and o.doc_no like \'M%\' and o.order_type !=10 and to_char(o.create_date,\'yyyy-mm-dd\')>=\'2016-01-01\'')
        num = ranNo(0, orderNo['DOC_NO'].__len__() - 1)
        doc_no = orderNo['DOC_NO'][num]

        status = '20'
        while status != '50':
            if not driver.find_element_by_id('btnSubmit').is_displayed():
                driver.find_element_by_class_name('open-close').click()
            time.sleep(0.5)
            driver.find_element_by_name('sp_docNo_LIKE').send_keys(doc_no)
            driver.find_element_by_id('btnSubmit').click()
            time.sleep(2)
            driver.find_element_by_xpath('//li[@id="accountmenu"]/a/i').click()
            driver.find_element_by_xpath('//li[@id="accountmenu"]/ul/li[1]/a').click()
            try:
                driver.find_element_by_xpath('//div[@id="jbox-state-state0"]/div[2]/button[1]').click()
                orderStatus = Oradao.sqlDiy(Oradao(), 'select * from om_orders o where o.doc_no=\'' + doc_no + '\'')
                status = orderStatus['ORDER_STATUS'][0]
            except:
                orderStatus = Oradao.sqlDiy(Oradao(), 'select * from om_orders o where o.doc_no=\'' + doc_no + '\'')
                status = orderStatus['ORDER_STATUS'][0]

        # 查询上面构造的那条交易完成的订单数据
        if not driver.find_element_by_id('btnSubmit').is_displayed():
            driver.find_element_by_class_name('open-close').click()
        time.sleep(0.5)
        driver.find_element_by_name('sp_docNo_LIKE').send_keys(doc_no)
        driver.find_element_by_id('btnSubmit').click()
        time.sleep(2)

        # 点击操作-申请退货
        driver.find_element_by_xpath('//li[@id="accountmenu"]/a/i').click()
        driver.find_element_by_xpath('//li[@id="accountmenu"]/ul/li[1]/a').click()

        # 订单明细-点击保存
        driver.switch_to_default_content()
        driver.execute_script('scrollTo(0,500)')
        driver.switch_to_frame('contentIframe1121')
        driver.find_element_by_id('btnSubmit').click()

        # 进入退货单管理页面
        driver.switch_to_default_content()
        driver.execute_script('scrollTo(0,0)')
        driver.switch_to_frame('contentIframe1121')

        # 取出退货单状态，验证是否为待审核
        rsCheckStatus = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td')[8].text
        self.assertEqual(rsCheckStatus, u'待审核')

        # 审核、入库、退款操作
        while rsCheckStatus != u'退货完成' and rsCheckStatus != u'取消退货':
            # 点击操作
            driver.find_element_by_xpath('//li[@id="accountmenu"]/a/i').click()
            # 审核
            if rsCheckStatus == u'待审核':

                driver.find_element_by_xpath('//li[@id="accountmenu"]/ul/li/a').click()
                flag = 1
            # 入库
            elif rsCheckStatus == u'待入库':
                driver.find_element_by_xpath('//li[@id="accountmenu"]/ul/li[1]/a').click()
                flag = 2
            # 退款
            else:
                driver.find_element_by_xpath('//li[@id="accountmenu"]/ul/li/a').click()
                driver.find_element_by_xpath('//div[@id="jbox-state-state0"]/div[2]/button[1]').click()
                flag = 3

            # 进入订单明细-随机选择成/入库完成/退款完成或取消退货-保存
            driver.switch_to_default_content()
            driver.execute_script('scrollTo(0,1000)')
            driver.switch_to_frame('contentIframe1121')
            checkNum = ranNo(1, 2)
            driver.find_element_by_xpath('//form[@id="inputForm"]/div/div[2]/div[6]/input['+str(checkNum)+']').click()
            driver.find_element_by_id('btnSubmit').click()
            time.sleep(2)

            # 筛选出审核/入库/退款后的订单，检查状态
            driver.switch_to_default_content()
            driver.execute_script('scrollTo(0,0)')
            driver.switch_to_frame('contentIframe1121')
            driver.find_element_by_name('sp_orders.docNo_LIKE').send_keys(doc_no)
            driver.find_element_by_id('btnSubmit').click()
            time.sleep(2)
            rsCheckStatus = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td')[8].text
            if checkNum == 2 and flag != 3:
                self.assertEqual(rsCheckStatus, u'取消退货')
            elif checkNum == 1 and flag == 1:
                self.assertEqual(rsCheckStatus, u'待入库')
            elif checkNum == 1 and flag == 2:
                self.assertEqual(rsCheckStatus, u'待退款')
            else:
                self.assertEqual(rsCheckStatus, u'退货完成')

if __name__ == '__main__':
    unittest.main()