# coding=utf-8

import unittest
import time
from selenium.webdriver.support.select import Select
from db.ora.oradao import Oradao
from util.boInitialize import BoInitialize
from util.ranchar import ranNo

__author__ = 'Maggie'


class BoAutoOrder(unittest.TestCase):
    def setUp(self):
        self.conf = BoInitialize(1)
        self.driver = self.conf.login()
        self.verificationErrors = []
        pass

    def tearDown(self):
        self.conf.getScreenshot(self)
        self.assertEqual([], self.verificationErrors)
        self.driver.quit()
        pass

    # 自动重消单

    def testBoAutoOrder(self):
        driver = self.driver
        conf = self.conf
        # 切换语言
        conf.boLangChange(driver, 'zh_CN')
        time.sleep(2)

        # 打开订单-自动重消单
        driver.find_element_by_xpath('//ul[@id="mainmenu"]/li[4]/a').click()
        driver.find_element_by_id('2189909').click()
        time.sleep(2)

        # 新增自动重消单
        if conf.env == 'sandbox':
            driver.get('https://sandbox-d-v1.jmtop.com/backOffice/autoOrder/autoOrderProductList')
        elif conf.env == 'production':
            driver.get('https://dist.jmtop.com/backOffice/autoOrder/autoOrderProductList')

        # 更新购物车
        driver.find_element_by_xpath('//form[@id="storeForm40"]/div/div/div/a').click()

        # 数据库随机取商品编码
        product = Oradao.sqlDiy(Oradao(),
                                'select s.id,p.product_no from pm_product_sale s,pm_product p where p.id=s.product_id and s.order_type=30 and s.company_code=\'' + conf.state + '\' and p.product_type=10 and s.del_flag=\'20\'')
        num = ranNo(0, product['ID'].__len__() - 1)
        product_id = product['ID'][num]
        product_no = product['PRODUCT_NO'][num]
        driver.find_element_by_name('sp_product.productNo_LIKE').send_keys(product_no)

        # 点击查询
        driver.find_element_by_id('btnSearch').click()
        time.sleep(2)

        # 加入购物车
        driver.find_element_by_id('cart'+str(product_id)).click()
        time.sleep(2)

        # 结算
        if conf.env == 'sandbox':
            driver.get('https://sandbox-d-v1.jmtop.com/backOffice/autoOrder/autoOrderProductList')
        elif conf.env == 'production':
            driver.get('https://dist.jmtop.com/backOffice/autoOrder/autoOrderProductList')

        # 下一步
        driver.find_element_by_id('addToCart_40').click()
        time.sleep(2)

        # 自提
        driver.find_element_by_id('isSelfPickup1').click()
        time.sleep(2)

        # 下一步
        driver.execute_script('scrollTo(0,1000)')
        driver.find_element_by_id('btnSubmit').click()
        time.sleep(2)

        # 填自动下单信息
        driver.find_element_by_id('description').send_keys('test')
        driver.find_element_by_id('nextRunDate').send_keys('2060-12-01')

        driver.find_element_by_id('cardHolderName').send_keys('test')
        driver.find_element_by_id('bankCardNo').send_keys('4444333322221111')
        Select(driver.find_element_by_name("expirationYear")).select_by_index(10)
        driver.find_element_by_id('securityCode').send_keys('123')

        driver.find_element_by_id('btnSubmit').click()
        time.sleep(2)

        # 提交订单
        driver.execute_script('scrollTo(0,1000)')
        driver.find_element_by_id('btnSubmit').click()
        driver.implicitly_wait(10)

        # 判断返回卡信息错误
        message = driver.find_element_by_class_name('toast-message').text[0:8]
        self.assertEqual(message, u'保存自动订单失败')

if __name__ == '__main__':
    unittest.main()