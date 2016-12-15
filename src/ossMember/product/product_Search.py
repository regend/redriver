# coding=utf-8
import unittest
from selenium.webdriver import ActionChains
import time
from db.ora.oradao import Oradao
from util.datview import getNum
from util.initialize import Initialize
from util.ranchar import ranNo

__author__ = 'Regend'


class ProductSearch(unittest.TestCase):
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

    def testProductSearch(self):
        # 初始化登录
        driver = self.driver
        conf = self.conf
        conf.stateChange(driver)
        driver.implicitly_wait(10)

        # 选择运营支撑平台
        driver.find_element_by_id('topMenu_1100').click()
        button = driver.find_element_by_id('left_menu_1110')
        menu = driver.find_element_by_class_name('nav-header')

        # 鼠标悬停在商品管理上
        chain = ActionChains(driver)
        chain.move_to_element(button).perform()
        driver.find_element_by_xpath('//li[@id="left_menu_1111"]/a/span').click()
        chain.move_to_element(menu).perform()

        driver.implicitly_wait(10)
        # 切换至iframe
        driver.switch_to_frame('contentIframe1111')

        product = Oradao.sqlDiy(Oradao(), 'select * from pm_product where DEL_FLAG = 0')
        num = ranNo(0, product['PRODUCT_NO'].__len__() - 1)
        product_no = product['PRODUCT_NO'][num]
        product_name = product['PRODUCT_NAME'][num]

        driver.find_element_by_name('sp_productNo_LIKE').send_keys(product_no)
        driver.find_element_by_id('btnSubmit').click()

        time.sleep(2)
        rsNum = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr').__len__()
        # test = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr')
        self.assertEquals(rsNum, 1)

        rsXpath = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr[' + str(rsNum) + ']/td')

        rsProductNo = rsXpath[0].text
        rsProductName = rsXpath[1].get_attribute('title')
        # rsProductKind = rsXpath[2].text
        # rsProductUnit = rsXpath[3].text
        # rsSaleKind = rsXpath[4].text

        # 断言
        self.assertEquals(rsProductNo, product['PRODUCT_NO'][num])
        self.assertEquals(rsProductName, product['PRODUCT_NAME'][num])

        driver.find_element_by_name('sp_productNo_LIKE').clear()
        driver.find_element_by_name('sp_productName_LIKE').send_keys(product_name)
        driver.find_element_by_id('btnSubmit').click()

        time.sleep(2)
        rsNum = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr').__len__()
        rs_tolal_num = getNum(driver.find_elements_by_xpath('//ul[@class="pagination"]/li')[-2].text)

        sqlCount = "select * from pm_product where DEL_FLAG = 0 and PRODUCT_NAME like \'%" + product_name + "%\'"
        sqlNum = Oradao.sqlCount(Oradao(), str(sqlCount))

        rsXpath = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr[' + str(rsNum) + ']/td')

        rsProductNo = rsXpath[0].text
        rsProductName = rsXpath[1].get_attribute('title')
        # rsProductKind = rsXpath[2].text
        # rsProductUnit = rsXpath[3].text
        # rsSaleKind = rsXpath[4].text

        # 断言
        self.assertEquals(rs_tolal_num, str(sqlNum))
        self.assertEquals(rsProductNo, product['PRODUCT_NO'][num])
        self.assertEquals(rsProductName, product['PRODUCT_NAME'][num])


if __name__ == '__main__':
    unittest.main()