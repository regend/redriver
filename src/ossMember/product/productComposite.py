# coding=utf-8
import unittest
from selenium.webdriver import ActionChains
from db.ora.oradao import Oradao
from util.datview import transData
from util.initialize import Initialize
from util.ranchar import ranNo

__author__ = 'Regend'


# 税率策略
class ProductComposite(unittest.TestCase):
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

    def testTax(self):
        # 初始化登录
        driver = self.driver
        conf = self.conf
        conf.stateChange(driver)
        driver.implicitly_wait(10)

        # 选择运营支撑平台
        driver.find_element_by_id('topMenu_1100').click()
        button = driver.find_element_by_id('left_menu_1110')
        menu = driver.find_element_by_class_name('nav-header')

        # 鼠标悬停在商品管理
        chain = ActionChains(driver)
        chain.move_to_element(button).perform()
        driver.find_element_by_xpath('//li[@id="left_menu_9214"]/a/span').click()
        chain.move_to_element(menu).perform()

        driver.implicitly_wait(10)
        # 切换至iframe
        driver.switch_to_frame('contentIframe9214')

        prdsql = 'select * from pm_composite_product'
        prodoctCom = Oradao.sqlDiy(Oradao(), prdsql)
        num = ranNo(0, prodoctCom['ID'].__len__()-1)
        productNo = prodoctCom['CODE'][num]
        productName = prodoctCom['NAME'][num]
        productType = transData('compositeProduct.type').get(prodoctCom['TYPE'][num])
        productNum = str(prodoctCom['QUATITY'][num])
        productMemo = prodoctCom['MEMO'][num]
        driver.find_element_by_name('sp_code_EQ').send_keys(productNo)
        driver.find_element_by_id('btnSubmit').click()

        driver.implicitly_wait(10)
        rsName = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr/td[1]').text
        rsCode = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr/td[2]').text
        rsType = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr/td[3]').text
        rsNum = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr/td[4]').text
        rsMemo = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr/td[5]').text

        self.assertEquals(productName, rsName)
        self.assertEquals(productNo, rsCode)
        self.assertEquals(productType, rsType)
        self.assertEquals(productNum, rsNum)
        self.assertEquals(productMemo, rsMemo)


if __name__ == '__main__':
    unittest.main()


