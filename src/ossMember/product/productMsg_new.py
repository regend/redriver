# coding=utf-8
import logging
import unittest
from selenium.webdriver import ActionChains
from db.ora.oradao import Oradao
from util.initialize import Initialize
from util.ranchar import ranNo, ranZNS, ranEN

__author__ = 'Regend'


class ProductNewMSG(unittest.TestCase):
    def setUp(self):
        self.conf = Initialize()
        self.driver = self.conf.start()
        self.verificationErrors = []
        pass

    def tearDown(self):
        self.conf.getScreenshot(self)
        self.assertEqual([], self.verificationErrors)
        logging.info(self.driver.page_source)
        self.driver.quit()
        pass

    def testProductMsgNew(self):
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
        driver.find_element_by_xpath('//li[@id="left_menu_7069"]/a/span').click()
        chain.move_to_element(menu).perform()

        driver.implicitly_wait(10)
        # 获取地区显示名以便最后断言使用
        state = conf.getState(driver)
        # 切换至iframe
        driver.switch_to_frame('contentIframe7069')

        # 点击新增
        driver.find_element_by_id('btnAdd').click()
        driver.implicitly_wait(10)

        # 选择商品编码
        driver.find_element_by_id('productNoButton').click()
        pdctFrame = driver.find_element_by_xpath('//div[@id="myWindow"]/iframe')
        driver.switch_to_frame(pdctFrame)

        # 随机选择商品编码
        product = Oradao().sqlDiy(
            'SELECT id,product_no,product_name FROM pm_product WHERE id NOT IN (SELECT product_id FROM pm_product_sale where company_code = \'' + conf.state + '\') AND id IN (SELECT product_id FROM pm_composite_product)')
        productLen = product['ID'].__len__() - 1
        ranList = ranNo(0, productLen)
        ranProductID = product['ID'][ranList]
        ranProductNo = product['PRODUCT_NO'][ranList]
        ranProductName = product['PRODUCT_NAME'][ranList]
        js = 'setParentValue(\'' + str(ranProductID) + '\',\'' + str(ranProductNo) + '\',\'' + str(
            ranProductName) + '\')'
        try:
            driver.execute_script(js)
        except EOFError:
            driver.get_screenshot_as_file('a.bmp')
        # 切回新增商品iframe
        driver.switch_to_default_content()
        driver.switch_to_frame('contentIframe7069')

        # 随机选择订单类型
        orderType = driver.find_elements_by_xpath('//select[@id="orderType"]/option')
        orderType[ranNo(0, orderType.__len__() - 1)].click()
        ranOrderType = driver.find_element_by_id('s2id_orderType').text

        # 输入随机商品销售名
        ranSaleName = ranZNS(4) + ranEN(4)
        driver.find_element_by_id('saleName').send_keys(ranSaleName)

        # 选择随机税率
        taxStrategy = driver.find_elements_by_xpath('//select[@name="taxStrategy"]/option')
        taxStrategy[ranNo(0, taxStrategy.__len__() - 1)].click()
        ranTaxStrategy = driver.find_element_by_xpath('//div[@id="s2id_autogen2"]/a/span').text

        # 选择状态
        status = driver.find_elements_by_xpath('//select[@name="delFlag"]/option')
        status[ranNo(0, status.__len__() - 1)].click()
        ranStatus = driver.find_element_by_xpath('//div[@id="s2id_autogen4"]/a/span').text

        # BV,PV,价格,折扣价
        ranBV = str(ranNo(100, 1000))
        driver.find_element_by_id('bv').send_keys(ranBV)
        ranPV = str(ranNo(100, 1000))
        driver.find_element_by_id('pv').send_keys(ranPV)
        ranAgio = str(ranNo(100, 1000))
        driver.find_element_by_id('agioPrice').send_keys(ranAgio)
        ranPrice = ranNo(10, 10000)
        driver.find_element_by_xpath('//div[@id="tabs"]/div[2]/div[1]/div/div[10]/div/span/input[1]').send_keys(
            ranPrice)
        driver.find_element_by_id('btnSubmit').click()

        driver.implicitly_wait(10)

        driver.find_element_by_name('sp_product.productNo_LIKE').send_keys(ranProductNo)
        driver.find_element_by_id('searchForm').submit()
        driver.implicitly_wait(10)
        rsNum = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr').__len__()
        rsXpath = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr[' + str(rsNum) + ']/td')

        # 获取查询结果各个字段值
        rsSaleName = rsXpath[1].text
        rsType = rsXpath[2].text
        rsCompanyCode = rsXpath[3].text
        rsProductNo = rsXpath[4].text
        rsPrice = rsXpath[5].text.replace(",", "")
        rsBV = rsXpath[6].text.replace(",", "")
        rsPV = rsXpath[7].text.replace(",", "")
        rsStatus = rsXpath[8].text.replace(",", "")

        # 断言
        self.assertEquals(rsSaleName, ranSaleName)
        self.assertEquals(rsType, ranOrderType)
        self.assertEquals(rsCompanyCode, state)
        self.assertEquals(rsProductNo, ranProductNo)
        self.assertEquals(rsPrice, "%.2f" % float(ranPrice))
        self.assertEquals(rsBV, "%.2f" % float(ranBV))
        self.assertEquals(rsPV, "%.2f" % float(ranPV))
        self.assertEquals(rsStatus, ranStatus)


if __name__ == '__main__':
    unittest.main()