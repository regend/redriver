# coding=utf-8
import unittest
from selenium.webdriver import ActionChains
import time
from selenium.webdriver.support.select import Select
from db.ora.oradao import Oradao
from util.initialize import Initialize
from util.ranchar import ranNo
from util.datview import getAreaIdByCode

__author__ = 'Maggie'


class OrderSave(unittest.TestCase):
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

    def testOrderSave(self):
        driver = self.driver
        conf = self.conf
        conf.stateChange(driver)
        driver.implicitly_wait(10)

        # OM002 下单&支付
        # 选择运营支撑平台
        driver.find_element_by_id('topMenu_1100').click()
        # 调用方法chooseMember
        self.count = 0
        self.chooseMember()
        # 支付
        self.pay()

    # 把如下操作放在方法chooseMember里，当出现条件限制执行不了的时候可调用多次重新选择其他会员编号
    def chooseMember(self):
        conf = self.conf
        driver = self.driver
        # 鼠标悬停在销售管理上
        button = driver.find_element_by_id('left_menu_1120')
        menu = driver.find_element_by_class_name('nav-header')
        chain = ActionChains(driver)
        chain.move_to_element(button).perform()
        driver.implicitly_wait(10)
        driver.find_element_by_xpath('//li[@id="left_menu_1121"]/a/span').click()
        chain.move_to_element(menu).perform()

        driver.implicitly_wait(10)

        # 切换至iframe
        driver.switch_to_frame('contentIframe1121')

        # 点击添加
        if not driver.find_element_by_id('btnAdd').is_displayed():
            driver.find_element_by_class_name('open-close').click()
        time.sleep(0.5)
        driver.find_element_by_id('btnAdd').click()

        # 切换至会员选择框的iframe
        driver.switch_to_frame('product')

        # 从数据库随机选择一个会员编号，当时生成环境时，则取名字含test的测试会员
        if conf.env == 'production':
            member = Oradao.sqlDiy(Oradao(),
                                   'select * from mm_member m where m.subtype=40 and m.status in (0,10) and m.company_code=\'' + conf.state + '\' and (m.name like \'%test%\' or m.name like \'%Test%\')')
        else:
            member = Oradao.sqlDiy(Oradao(),
                                   'select * from mm_member m where m.subtype=40 and m.company_code=\'' + conf.state + '\' and m.status in (0,10)')

        num = ranNo(0, member['MEMBER_NO'].__len__() - 1)
        member_no = member['MEMBER_NO'][num]
        member_grade = member['ENROLLMENT_GRADE'][num]

        # 取到的会员编号放到页面查询，点击选择
        driver.find_element_by_name('sp_memberNo_LIKE').send_keys(member_no)
        driver.find_element_by_id('btnSubmit').click()
        time.sleep(2)
        try:
            driver.find_element_by_xpath('//table[@id="treeTable1"]/tbody/tr/td[1]/a').click()
        except:
            driver.find_element_by_xpath('//table[@id="treeTable1"]/tbody/tr/td[1]/a').click()

        # 切换至iframe(先跳到最初始的iframe，再进入)
        driver.switch_to_default_content()
        driver.switch_to_frame('contentIframe1121')

        # 选择单品
        # driver.find_element_by_id('s2id_productType').click()
        # driver.find_element_by_xpath('//select[@id="productType"]/option[2]').click()

        # 随机选择 订单类型
        driver.find_element_by_id('s2id_orderType').click()
        orderTypeNum = ranNo(2, driver.find_elements_by_xpath('//select[@id="orderType"]/option').__len__())
        driver.find_element_by_xpath('//select[@id="orderType"]/option[' + str(orderTypeNum) + ']').click()
        time.sleep(2)
        orderType = driver.find_element_by_xpath(
            '//select[@id="orderType"]/option[' + str(orderTypeNum) + ']').get_attribute('value')

        # 判断是否有收货地址,若有则随机选择一个收货地址，没则选择自提
        address = Oradao.sqlDiy(Oradao(),
                                'select * from mm_member_address ma where ma.member_id in (select m.id from mm_member m where m.member_no=\'' + member_no + '\') and ma.country=' + getAreaIdByCode(
                                    conf.state))
        addressLen = address['ID'].__len__()
        if addressLen > 0:
            addressNum = ranNo(1, addressLen)
            driver.find_element_by_xpath(
                '//table[@id="treeTable1"]/tbody/tr[' + str(addressNum) + ']/td[1]/input').click()
        else:
            driver.find_element_by_id('isSelfPickup').click()

        # 根据不同订单类型与会员级别，循环添加商品直到bv>=50bv，>=300,>=400,>=500
        product = Oradao.sqlDiy(Oradao(),
                                'select p.id,p.product_id,p.bv,pm.product_no from pm_product_sale p,pm_product pm where pm.id=p.product_id and pm.product_type=\'10\' and p.order_type=\'' + orderType + '\' and p.company_code=\'' + conf.state + '\' and p.del_flag=\'20\'')
        bv = 0
        if orderType == '10':
            while bv < 50:
                product_num = ranNo(0, product['ID'].__len__() - 1)
                product_id = product['ID'][product_num]
                product_no = product['PRODUCT_NO'][product_num]
                # 按商品编码查询
                driver.find_element_by_id('productNo').send_keys(product_no)
                # 点击查询商品
                driver.find_element_by_id('btnSearch').click()
                driver.implicitly_wait(10)
                driver.find_element_by_id('buy-s-' + str(product_id)).click()
                bv = bv + product['BV'][product_num]
                driver.find_element_by_id('productNo').clear()

        elif orderType == '20' and member_grade == '10':
            while bv < 300:
                product_num = ranNo(0, product['ID'].__len__() - 1)
                product_id = product['ID'][product_num]
                product_no = product['PRODUCT_NO'][product_num]
                # 按商品编码查询
                driver.find_element_by_id('productNo').send_keys(product_no)
                # 点击查询商品
                driver.find_element_by_id('btnSearch').click()
                driver.implicitly_wait(10)
                driver.find_element_by_id('buy-s-' + str(product_id)).click()
                bv = bv + product['BV'][product_num]
                driver.find_element_by_id('productNo').clear()

        elif orderType == '20' and member_grade == '20':
            while bv < 400:
                product_num = ranNo(0, product['ID'].__len__() - 1)
                product_id = product['ID'][product_num]
                product_no = product['PRODUCT_NO'][product_num]
                # 按商品编码查询
                driver.find_element_by_id('productNo').send_keys(product_no)
                # 点击查询商品
                driver.find_element_by_id('btnSearch').click()
                driver.implicitly_wait(10)
                driver.find_element_by_id('buy-s-' + str(product_id)).click()
                bv = bv + product['BV'][product_num]
                driver.find_element_by_id('productNo').clear()

        elif orderType == '20' and member_grade == '30':
            while bv < 500:
                product_num = ranNo(0, product['ID'].__len__() - 1)
                product_id = product['ID'][product_num]
                product_no = product['PRODUCT_NO'][product_num]
                # 按商品编码查询
                driver.find_element_by_id('productNo').send_keys(product_no)
                # 点击查询商品
                driver.find_element_by_id('btnSearch').click()
                driver.implicitly_wait(10)
                driver.find_element_by_id('buy-s-' + str(product_id)).click()
                bv = bv + product['BV'][product_num]
                driver.find_element_by_id('productNo').clear()

        else:
            product_num = ranNo(0, product['ID'].__len__() - 1)
            product_id = product['ID'][product_num]
            product_no = product['PRODUCT_NO'][product_num]
            # 按商品编码查询
            driver.find_element_by_id('productNo').send_keys(product_no)
            # 点击查询商品
            driver.find_element_by_id('btnSearch').click()
            driver.implicitly_wait(10)
            driver.find_element_by_id('buy-s-' + str(product_id)).click()

        # 移动滚动条，避免按钮被遮住，需先切换iframe（滚动条属于最外面那层的）
        driver.switch_to_default_content()
        driver.execute_script('scrollTo(0,0)')

        # 再切回里面的iframe
        driver.switch_to_frame('contentIframe1121')

        # 点击右侧的购物车，再点击结账
        driver.find_element_by_id('shopCart').click()
        time.sleep(2)
        driver.find_element_by_id('goShopping').click()
        time.sleep(2)

        try:
            # 如果选择的会员能正常下单，则进入到订单信息页，点击保存按钮
            driver.switch_to_default_content()
            driver.execute_script('scrollTo(0,10000)')
            driver.switch_to_frame('contentIframe1121')
            driver.find_element_by_id('btnSubmit').click()
            time.sleep(2)
        except:
            # 如果会员下不了单，页面滚动到最顶
            driver.switch_to_default_content()
            driver.execute_script('scrollTo(0,0)')
            # 关闭订单管理页面
            driver.find_element_by_xpath('//div[@id="tt"]/div[1]/div[3]/ul/li[2]/a[2]').click()
            # 重新下单选择会员
            self.chooseMember()

        # 点击订单明细页的保存按钮
        driver.find_element_by_id('btnSubmit').click()
        time.sleep(5)

        try:
            # 能正常下单，则会进入支付页面
            driver.switch_to_default_content()
            driver.execute_script('scrollTo(0,0)')
            driver.switch_to_frame('contentIframe1121')
            driver.find_element_by_xpath('//form[@id="payForm"]/div[2]/div').text
        except:
            # 如果会员存在待支付的首购单则下不了单，关闭订单管理页面
            driver.switch_to_default_content()
            driver.find_element_by_xpath('//div[@id="tt"]/div[1]/div[3]/ul/li[2]/a[2]').click()
            # 重新下单选择会员
            self.count += 1
            # 当出现10次都下不了单时，抛出异常，排除是否代码问题
            if self.count >= 10:
                raise Exception(u'下单错误')
            self.chooseMember()

    # 支付操作
    def pay(self):
        driver = self.driver
        conf = self.conf

        # 若生产环境，则选在线支付（填不存在的信用卡，使其支付不成功即可）
        if conf.env == 'production':
            # 在线支付
            driver.find_element_by_xpath('//form[@id="payForm"]/div[4]/div/p[6]/input[1]').click()
            time.sleep(1)
            driver.find_element_by_name('onlineMode').click()
            time.sleep(1)
            # 填信用卡号
            credit_card = str(ranNo(6000000000000000, 6999999999999999))
            driver.find_element_by_id('creditcard_number').send_keys(credit_card)
            # 选有效期
            driver.find_element_by_xpath('//div[@id="s2id_creditcard_expireMonth"]/a/div/b').click()
            Select(driver.find_element_by_id("creditcard_expireMonth")).select_by_index(ranNo(0, 11))
            driver.find_element_by_xpath('//div[@id="s2id_creditcard_expireYear"]/a/div/b').click()
            Select(driver.find_element_by_id("creditcard_expireYear")).select_by_index(ranNo(1, 9))
            # 输入安全码
            driver.find_element_by_id('creditcard_cvv2').send_keys(str(ranNo(100, 999)))
            # 持卡人姓名
            driver.find_element_by_id('creditcard_firstName').send_keys('test')
            driver.find_element_by_id('creditcard_lastName').send_keys(str(ranNo(1, 99)))
            # 邮编
            driver.find_element_by_id('creditcard_zip').send_keys(str(ranNo(10000, 99999)))
            # 地址
            driver.find_element_by_id('creditcard_address1').send_keys('test' + str(ranNo(1, 999)))

            # 点击支付
            driver.switch_to_default_content()
            driver.execute_script('scrollTo(0,200)')
            driver.switch_to_frame('contentIframe1121')
            driver.find_element_by_id('btnSubmit').click()
            time.sleep(2)

            # 判断返回卡信息错误
            driver.switch_to_default_content()
            driver.execute_script('scrollTo(0,0)')
            driver.switch_to_frame('contentIframe1121')
            message = driver.find_element_by_xpath('//div[@class="form-actions"]/p').text
            self.assertEqual(message, u'Invalid CARDNUMBER field')

        # 测试环境（test&sandbox），则选现金支付
        else:
            # 选择现金支付
            driver.find_element_by_xpath('//form[@id="payForm"]/div[4]/div/p[1]/input[1]').click()
            time.sleep(2)

            # 点击支付
            driver.switch_to_default_content()
            driver.execute_script('scrollTo(0,200)')
            driver.switch_to_frame('contentIframe1121')
            driver.find_element_by_id('btnSubmit').click()

            # 点击返回
            driver.switch_to_default_content()
            driver.execute_script('scrollTo(0,0)')
            driver.switch_to_frame('contentIframe1121')
            driver.find_element_by_id('btnSubmit').click()

            # 从数据库搜索新增的订单编号
            order = Oradao.sqlDiy(Oradao(),
                                  'select * from om_orders o where o.company_code=\'' + conf.state + '\' order by o.doc_no desc')
            docNo = order['DOC_NO'][0]

            # 获取页面查询到的订单号
            rsDocNo = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td[2]')[0].text

            # 断言
            self.assertEquals(rsDocNo, docNo)


if __name__ == '__main__':
    unittest.main()