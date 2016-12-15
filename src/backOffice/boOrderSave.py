# coding=utf-8

import unittest
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.support.select import Select
from db.ora.oradao import Oradao
from util.boInitialize import BoInitialize
from util.datview import getAreaIdByCode
from util.ranchar import ranNo

__author__ = 'Maggie'


class BoOrderSave(unittest.TestCase):
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

    # bo004 & bo006 下单&支付
    def testBoOrderSave(self):
        driver = self.driver
        conf = self.conf
        # 切换语言
        conf.boLangChange(driver, 'zh_CN')
        # 声明member对象
        member = conf.member
        time.sleep(2)

        # 打开订单-我要下单
        driver.find_element_by_xpath('//ul[@id="mainmenu"]/li[4]/a').click()
        time.sleep(2)
        driver.find_element_by_id('8091').click()
        driver.implicitly_wait(5)

        # 当前会员编号/级别
        member_no = member['MEMBER_NO']
        member_grade = member['ENROLLMENT_GRADE']

        # 下单
        if member_grade == '0':
            order_status = driver.find_element_by_xpath('//form[@id="storeForm10"]/div/div/ul/li').text[-3:]
            # 当存在首购单待支付，则先支付再下升级或重消单
            if order_status == u'待支付':
                # 订单号
                order_no = driver.find_element_by_xpath('//form[@id="storeForm10"]/div/div/ul/li').text[0:16]

                # 订单金额
                order_amount = Oradao.sqlDiy(Oradao(), 'select * from om_orders o where o.doc_no=\'' + order_no + '\'')[
                    'TOTAL_NET_AMOUNT'][0]
                # 会员电子钱包余额
                wm_value = Oradao.sqlDiy(Oradao(),
                                         'select * from wm_finance_info f where f.account=\'' + member_no + '\'and f.ewallet_type=1')[
                    'TOTAL_EWALLET_VALUE'][0]

                # 电子钱包充值
                if order_amount > wm_value:
                    self.wm_fund_in()

                # 点击我的订单
                driver.find_element_by_xpath('//ul[@id="mainmenu"]/li[4]/a').click()
                time.sleep(2)
                driver.find_element_by_id('28718').click()
                driver.implicitly_wait(5)

                # 查询待支付订单
                driver.find_element_by_name('sp_docNo_LIKE').send_keys(order_no)
                driver.find_element_by_id('btnSubmit').click()
                time.sleep(2)

                # 去支付
                driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr/td[8]/a[1]').click()
                time.sleep(2)

                # 支付操作
                driver.switch_to_frame('payIframe')
                self.pay()

                # 首购支付完成，重新进入 我要下单
                driver.find_element_by_xpath('//ul[@id="mainmenu"]/li[4]/a').click()
                time.sleep(2)
                driver.find_element_by_id('8091').click()
                driver.implicitly_wait(5)

                # 完成首购支付后，进行升级/重消单操作
                self.order()

            # 不存在待支付首购单，直接进行首购单操作
            else:
                self.order()

        # 下升级/重消单
        else:
            self.order()

    def order(self):
        driver = self.driver
        conf = self.conf
        member = conf.member
        member_no = member['MEMBER_NO']
        member_id = member['ID']

        # 会员级别
        member_grade = Oradao.sqlDiy(Oradao(), 'select * from mm_member m where m.member_no=\'' + member_no + '\'')[
            'ENROLLMENT_GRADE'][0]

        # 会员电子钱包余额
        wm_value = Oradao.sqlDiy(Oradao(),
                                 'select * from wm_finance_info f where f.account=\'' + member_no + '\'and f.ewallet_type=1')[
            'TOTAL_EWALLET_VALUE'][0]

        # 下单-根据当前会员级别，确定下单类型
        if member_grade == '0':
            # 点击下首购单
            order_type = 10
            driver.find_element_by_xpath('//form[@id="storeForm10"]/div/div/div[3]/a').click()

        elif member_grade == '40':
            # 点击下重消单
            order_type = 30
            driver.find_element_by_xpath('//form[@id="storeForm30"]/div/div/div[3]/a').click()

        else:
            num = ranNo(2, 3)
            # 随机下升级或重消单
            driver.find_element_by_xpath('//form[@id="storeForm' + str(num) + '0"]/div/div/div[3]/a').click()
            if num == 2:
                order_type = 20
            else:
                order_type = 30

        # 购物车商品数量，非0时，先清空
        # count = driver.find_element_by_xpath('//div[@id="spc-tooltip"]/span').text
        shopping = Oradao.sqlDiy(Oradao(), 'select * from BO_SHOPPING_CART s where s.member_id=' + str(member_id) + 'and s.order_type=' + str(order_type))
        count = shopping['ID'].__len__()-1
        if count != '0':
            # 鼠标移动到购物车上
            chain = ActionChains(driver)
            chain.move_to_element(driver.find_element_by_id('spc-tooltip')).perform()
            driver.implicitly_wait(10)
            # 清空购物车
            for i in range(0, count+1):
                driver.find_element_by_xpath('//li[@id="li' + str(shopping['ID'][i]) + '"]/div[3]/a').click()
            driver.implicitly_wait(10)

        # 数据库取商品
        product = Oradao.sqlDiy(Oradao(),
                                'select p.id,p.product_id,pm.product_no,p.bv from pm_product_sale p,pm_product pm where pm.id=p.product_id and pm.product_type=\'10\' and p.order_type=' + str(
                                    order_type) + ' and p.company_code=\'' + conf.state + '\' and p.del_flag=\'20\'')

        # 循环把商品加入购物车，直到满足下单的bv数
        bv = 0
        if order_type == 10:
            while bv < 50:
                product_num = ranNo(0, product['ID'].__len__() - 1)
                product_no = product['PRODUCT_NO'][product_num]
                product_id = product['ID'][product_num]
                # 输入商品编码-点击查询
                driver.find_element_by_name('sp_product.productNo_LIKE').send_keys(product_no)
                driver.find_element_by_id('btnSearch').click()
                time.sleep(2)
                # 加入购物车
                driver.find_element_by_id('cart' + str(product_id)).click()
                time.sleep(2)
                bv = bv + product['BV'][product_num]
                driver.find_element_by_name('sp_product.productNo_LIKE').clear()

        elif order_type == 20 and member_grade == '10':
            while bv < 300:
                product_num = ranNo(0, product['ID'].__len__() - 1)
                product_no = product['PRODUCT_NO'][product_num]
                product_id = product['ID'][product_num]
                # 输入商品编码-点击查询
                driver.find_element_by_name('sp_product.productNo_LIKE').send_keys(product_no)
                driver.find_element_by_id('btnSearch').click()
                time.sleep(2)
                # 加入购物车
                driver.find_element_by_id('cart' + str(product_id)).click()
                time.sleep(2)
                bv = bv + product['BV'][product_num]
                driver.find_element_by_name('sp_product.productNo_LIKE').clear()

        elif order_type == 20 and member_grade == '20':
            while bv < 400:
                product_num = ranNo(0, product['ID'].__len__() - 1)
                product_no = product['PRODUCT_NO'][product_num]
                product_id = product['ID'][product_num]
                # 输入商品编码-点击查询
                driver.find_element_by_name('sp_product.productNo_LIKE').send_keys(product_no)
                driver.find_element_by_id('btnSearch').click()
                time.sleep(2)
                # 加入购物车
                driver.find_element_by_id('cart' + str(product_id)).click()
                time.sleep(2)
                bv = bv + product['BV'][product_num]
                driver.find_element_by_name('sp_product.productNo_LIKE').clear()

        elif order_type == 20 and member_grade == '30':
            while bv < 500:
                product_num = ranNo(0, product['ID'].__len__() - 1)
                product_no = product['PRODUCT_NO'][product_num]
                product_id = product['ID'][product_num]
                # 输入商品编码-点击查询
                driver.find_element_by_name('sp_product.productNo_LIKE').send_keys(product_no)
                driver.find_element_by_id('btnSearch').click()
                time.sleep(2)
                # 加入购物车
                driver.find_element_by_id('cart' + str(product_id)).click()
                time.sleep(2)
                bv = bv + product['BV'][product_num]
                driver.find_element_by_name('sp_product.productNo_LIKE').clear()

        else:
            product_num = ranNo(0, product['ID'].__len__() - 1)
            product_no = product['PRODUCT_NO'][product_num]
            product_id = product['ID'][product_num]
            # 输入商品编码-点击查询
            driver.find_element_by_name('sp_product.productNo_LIKE').send_keys(product_no)
            driver.find_element_by_id('btnSearch').click()
            time.sleep(2)
            # 加入购物车
            driver.find_element_by_id('cart' + str(product_id)).click()
            time.sleep(2)

        # 结算
        if conf.env == 'sandbox':
            driver.get('https://sandbox-d-v1.jmtop.com/backOffice/order/goToShoppingCart')
        elif conf.env == 'production':
            driver.get('https://dist.jmtop.com/backOffice/order/goToShoppingCart')
        driver.implicitly_wait(10)
        driver.find_element_by_id('addToCart_' + str(order_type)).click()
        time.sleep(2)

        # 判断是否有收货地址,若有则随机选择一个收货地址，没则选择自提
        address = Oradao.sqlDiy(Oradao(),
                                'select * from mm_member_address ma where ma.member_id in (select m.id from mm_member m where m.member_no=\'' + member_no + '\') and ma.country=' + getAreaIdByCode(
                                    conf.state))
        address_len = address['ID'].__len__()
        if address_len > 0:
            address_num = ranNo(0, address_len - 1)
            address_id = address['ID'][address_num]
            driver.find_element_by_xpath('//tr[@id="' + str(address_id) + '_tr"]/td[1]/input').click()
        else:
            driver.find_element_by_id('isSelfPickup').click()

        # 订单金额
        order_amount = float(driver.find_element_by_id('subTotal').text.replace(',', ''))

        # 电子钱包充值
        if order_amount > wm_value:
            self.wm_fund_in()

        # 点击保存
        driver.implicitly_wait(10)
        driver.execute_script('scrollTo(0,500)')
        driver.find_element_by_id('btnSubmit').click()

        # 订单信息页-点击保存
        driver.implicitly_wait(10)
        driver.execute_script('scrollTo(0,500)')
        driver.find_element_by_id('btnSubmit').click()
        time.sleep(2)

        # 支付操作
        driver.switch_to_frame('payIframe')
        self.pay()

        # 点击我的订单
        driver.find_element_by_xpath('//ul[@id="mainmenu"]/li[4]/a').click()
        driver.find_element_by_id('28718').click()
        time.sleep(2)

        # 页面按订单号排序
        driver.find_element_by_xpath('//table[@id="contentTable"]/thead/tr/th[1]').click()
        time.sleep(2)
        driver.find_element_by_xpath('//table[@id="contentTable"]/thead/tr/th[1]').click()
        time.sleep(2)

        # 页面取新订单号
        rs_doc_no = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td[1]/a').text

        # 数据库取新订单号
        order = Oradao.sqlDiy(Oradao(), 'select * from om_orders o where o.member_id =\'' + str(
            member_id) + '\'order by o.doc_no desc')

        # 断言
        self.assertEqual(rs_doc_no, order['DOC_NO'][0])

    def wm_fund_in(self):
        driver = self.driver
        conf = self.conf
        member = conf.member
        member_no = member['MEMBER_NO']

        # 切换到原始窗口(oss窗口)
        driver.switch_to_window(driver.window_handles[0])
        driver.implicitly_wait(10)
        # 选择运营支撑平台
        driver.switch_to_default_content()
        driver.find_element_by_id('topMenu_1100').click()
        # 鼠标悬停在电子钱包上
        chain = ActionChains(driver)
        chain.move_to_element(driver.find_element_by_id('left_menu_73')).perform()
        driver.implicitly_wait(10)
        driver.find_element_by_xpath('//li[@id="left_menu_85"]/a/span').click()
        chain.move_to_element(driver.find_element_by_class_name('nav-header')).perform()
        driver.implicitly_wait(10)
        # 切换至iframe
        driver.switch_to_frame('contentIframe85')
        # 点击添加
        driver.find_elements_by_id('btnSubmit')[1].click()
        time.sleep(2)
        # 选择钱包账户
        driver.find_element_by_id('selectAccount').click()
        driver.switch_to_frame('jbox-iframe')
        driver.find_element_by_name('sp_memberCode_like').send_keys(member_no)
        driver.find_element_by_id('btnSubmit').click()
        time.sleep(2)
        driver.find_element_by_xpath('//table[@id="treeTable1"]/tbody/tr/td[1]/a').click()
        # 输入充值金额
        driver.switch_to_default_content()
        driver.switch_to_frame('contentIframe85')
        driver.find_element_by_id('ewalletValue').clear()
        driver.find_element_by_id('ewalletValue').send_keys(999999)
        # 选择账户类型为电子钱包
        driver.find_element_by_xpath('//div[@id="s2id_autogen1"]/a/div/b').click()
        Select(driver.find_element_by_name("ewalletType")).select_by_index(1)
        # 备注
        driver.find_element_by_id('remark').send_keys(u'充值')
        # 保存
        driver.find_element_by_id('btnSubmit').click()
        time.sleep(2)
        # 审核
        driver.find_element_by_id('sp_financeInfo.memberCode_LIKE').send_keys(member_no)
        driver.find_element_by_id('btnSubmit').click()
        time.sleep(2)
        driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr/td[13]/a[3]').click()
        time.sleep(2)
        driver.find_element_by_id('btnSubmit').click()
        time.sleep(2)
        # 切换到bo窗口
        driver.switch_to_window(driver.window_handles[1])
        driver.implicitly_wait(10)

    # 支付
    def pay(self):
        driver = self.driver

        # 选择电子钱包付款
        driver.find_element_by_name('payType').click()

        # 输入支付密码
        driver.find_element_by_id('paypwd').send_keys('123456')

        # 点击支付
        driver.find_element_by_id('btnSubmit').click()
        time.sleep(2)

        # 跳出支付iframe
        driver.switch_to_default_content()


if __name__ == '__main__':
    unittest.main()