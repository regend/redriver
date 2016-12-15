# coding=utf-8
import unittest
from selenium.webdriver import ActionChains
import time
from db.ora.oradao import Oradao
from util.initialize import Initialize
from util.ranchar import ranNo

__author__ = 'Maggie'


class OrderChangeAdd(unittest.TestCase):
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

    def testOrderChangeAdd(self):
        driver = self.driver
        conf = self.conf
        state = conf.state
        conf.stateChange(driver)
        driver.implicitly_wait(10)

        # OM004 换货单管理-添加

        # 先构造一条交易完成的订单数据(待发货--》交易完成)
        driver.find_element_by_id('topMenu_1100').click()
        button = driver.find_element_by_id('left_menu_1120')
        menu = driver.find_element_by_class_name('nav-header')

        chain = ActionChains(driver)
        chain.move_to_element(button).perform()
        driver.implicitly_wait(10)
        time.sleep(2)
        driver.find_element_by_xpath('//li[@id="left_menu_1121"]/a/span').click()
        chain.move_to_element(menu).perform()
        driver.implicitly_wait(10)
        driver.switch_to_frame('contentIframe1121')

        orderNo = Oradao.sqlDiy(Oradao(),
                                'select * from om_orders o where o.company_code=\'' + state + '\'and o.order_status=20 and o.doc_no like \'M%\'and to_char(o.create_date,\'yyyy-mm-dd\')>=\'2016-01-01\'')
        num = ranNo(0, orderNo['DOC_NO'].__len__() - 1)
        orderType = orderNo['ORDER_TYPE'][num]

        status = '20'
        while status != '50':
            doc_no = orderNo['DOC_NO'][num]
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

        # 进行换货单操作
        # 鼠标悬停在销售管理上
        driver.switch_to_default_content()
        button = driver.find_element_by_id('left_menu_1120')
        menu = driver.find_element_by_class_name('nav-header')

        chain = ActionChains(driver)
        chain.move_to_element(button).perform()
        driver.implicitly_wait(10)

        # 选择换货单管理
        driver.find_element_by_xpath('//li[@id="left_menu_28740"]/a/span').click()
        chain.move_to_element(menu).perform()

        driver.implicitly_wait(10)
        # 切换至iframe
        driver.switch_to_frame('contentIframe28740')

        # 点击添加
        driver.find_element_by_id('btnAdd').click()
        time.sleep(2)

        # 点击选择原订单号
        driver.find_element_by_id('memberIdButton').click()

        # 切换至订单选择框的iframe
        driver.switch_to_frame('jbox-iframe')

        # 用构造好的交易完成的订单进行换货,放到页面查询，点击选择
        driver.find_element_by_name('sp_docNo_EQ').send_keys(doc_no)
        driver.find_element_by_id('btnSubmit').click()
        time.sleep(2)
        driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr/td[1]/a').click()

        # 获取退回商品的BV、数量与原订单状态
        driver.switch_to_default_content()
        driver.switch_to_frame('contentIframe28740')
        len = driver.find_elements_by_xpath('//table[@id="table1"]/tbody/tr').__len__()
        total_bv = 0
        for i in range(1, len+1):
            cBv = driver.find_elements_by_xpath('//table[@id="table1"]/tbody/tr['+str(i)+']/td')[3].text
            cCount = driver.find_elements_by_xpath('//table[@id="table1"]/tbody/tr['+str(i)+']/td[6]/input')[0].get_attribute('value')
            total_bv = total_bv + int(cBv) * int(cCount)

        # 选择换货商品
        driver.find_element_by_id('productButton').click()

        # 切换至商品选择框的iframe
        driver.switch_to_frame('jbox-iframe')

        # 循环添加退回商品直到bv>=原订单商品(从数据库随机退回商品编号，放到页面查询，点击选择)
        product = Oradao.sqlDiy(Oradao(),
                                'select * from pm_product_sale p,pm_product pp where p.product_id=pp.id and p.company_code=\'' + state + '\'and p.order_type=\'' + orderType + '\'and p.del_flag=\'20\' and pp.product_type=10')
        bv = 0
        while bv < total_bv:
            num = ranNo(0, product['ID'].__len__() - 1)
            productNo = product['PRODUCT_NO'][num]

            driver.find_element_by_name('sp_product.productNo_LIKE').send_keys(productNo)
            driver.find_element_by_id('btnSubmit').click()
            time.sleep(2)
            try:
                driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr/td[1]/a').click()
                bv = bv + int(product['BV'][num])
                driver.find_element_by_name('sp_product.productNo_LIKE').clear()
            except:
                driver.find_element_by_name('sp_product.productNo_LIKE').clear()

        # 移动最外层滚动条，关闭选择商品框
        driver.switch_to_default_content()
        driver.execute_script('scrollTo(0,300)')
        driver.switch_to_frame('contentIframe28740')
        driver.find_element_by_xpath('//div[@id="jbox-state-state0"]/div[2]/button').click()
        driver.implicitly_wait(10)

        # 点击结算
        # driver.switch_to_default_content()
        # driver.execute_script('scrollTo(0,0)')
        # driver.switch_to_frame('contentIframe28740')
        driver.find_element_by_id('btnSubmit').click()

        # 点击保存
        driver.switch_to_default_content()
        driver.execute_script('scrollTo(0,5000)')
        driver.switch_to_frame('contentIframe28740')
        price = driver.find_element_by_id('subTotal').text
        driver.find_element_by_id('btnSubmit').click()
        time.sleep(2)

        # 页面滚动到最顶
        driver.switch_to_default_content()
        driver.execute_script('scrollTo(0,0)')
        driver.switch_to_frame('contentIframe28740')

        # 但应付金额大于0时，则选择现金进行支付操作
        if price > '0.00':
            driver.find_element_by_xpath('//form[@id="payForm"]/div[4]/div/p[1]/input[1]').click()
            driver.find_element_by_id('btnSubmit').click()
            time.sleep(2)
            # 支付成功，点击返回
            driver.find_element_by_id('btnSubmit').click()
            driver.implicitly_wait(10)

        # 断言
        # 按原订单号进行查询，获取页面查询到的换货订单号
        if not driver.find_element_by_id('btnSubmit').is_displayed():
            driver.find_element_by_name('sp_orders.docNo_LIKE').send_keys(doc_no)
        driver.find_element_by_id('btnSubmit').click()
        time.sleep(2)
        rsDocNo = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td[1]/a[1]').text

        # 从数据库搜索新增的换货订单编号
        change_order = Oradao.sqlDiy(Oradao(),
                                     'select * from om_change_orders co where co.company_code=\'' + state + '\' order by co.doc_no desc')
        docNo = change_order['DOC_NO'][0]

        self.assertEquals(rsDocNo, docNo)


if __name__ == '__main__':
    unittest.main()