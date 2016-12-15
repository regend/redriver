# coding=utf-8
import unittest
from selenium.webdriver import ActionChains
from db.ora.oradao import Oradao
from util.initialize import Initialize
from util.ranchar import ranNo, ranZNS, ranEN

__author__ = 'Regend'


class ProductMsgSearch(unittest.TestCase):
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

    def testProductMsg(self):
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
        # 切换至iframe
        driver.switch_to_frame('contentIframe7069')

        # 计算数据数量
        pageSize = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr').__len__()
        pageCount = pageSize
        # -2:除去上一页和下一页
        pageNo = int(driver.find_elements_by_xpath('/html/body/div/div/div/ul/li/a')[-2].text)
        if pageNo > 1:
            driver.find_element_by_link_text(str(pageNo)).click()
            driver.implicitly_wait(10)
            lastPageSize = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr').__len__()
            pageCount = pageSize * (pageNo - 1) + lastPageSize
            driver.find_element_by_link_text('1').click()

        # 测试商品信息数量
        sqlCount = Oradao().sqlCount('select * from pm_product_sale where company_code=\'' + conf.state + '\'')

        # 断言
        self.assertEquals(sqlCount, pageCount)

        # 测试根据商品编码查询
        productMsg = Oradao().sqlDiy(
            'select pps.ORDER_TYPE as ORDER_TYPE,pp.PRODUCT_NAME as PRODUCT_NAME,pp.PRODUCT_NO as PRODUCT_NO,pps.DEL_FLAG as DEL_FLAG,pps.SALE_NAME as SALE_NAME,'
            'pps.COMPANY_CODE as COMPANY_CODE,pps.PRICE as PRICE,pps.BV as BV,pps.PV as PV from pm_product_sale pps,pm_product pp '
            'where pps.PRODUCT_ID = pp.ID and pps.COMPANY_CODE = \'' + conf.state + '\'')
        productMsgLen = productMsg['PRODUCT_NO'].__len__()
        productMsgNo = productMsg['PRODUCT_NO'][ranNo(0, productMsgLen - 1)]
        driver.find_element_by_name('sp_product.productNo_LIKE').send_keys(productMsgNo)
        driver.find_element_by_id('btnSubmit').click()

        rsCount = driver.find_elements_by_xpath('//table[@id="contentTable1"]/tbody/tr')
        # 对每一列进行检查
        for i in range(1, rsCount.__len__() + 1):
            rsProductNo = driver.find_element_by_xpath(
                '//table[@id="contentTable"]/tbody/tr[' + str(i) + ']/td[4]/span')
            self.assertIn(productMsgNo, rsProductNo.text)
        pageNo = int(driver.find_elements_by_xpath('/html/body/div/div/div/ul/li/a')[-2].text)

        # 对每一页的每一列进行检查
        if pageNo > 1:
            for i in range(2, pageNo + 1):
                driver.find_element_by_link_text(str(i)).click()
                driver.implicitly_wait(10)
                rsCount = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr')
                for n in range(1, rsCount.__le__() + 1):
                    rsProductNo = driver.find_elements_by_xpath(
                        '//table[@id="contentTable"]/tbody/tr[' + str(n) + ']/td[4]/span')
                    self.assertIn(productMsgNo, rsProductNo[n].text)

        # 对订单类型检查
        driver.find_element_by_name('sp_product.productNo_LIKE').clear()
        orderTypeSelect = driver.find_elements_by_xpath('//form[@id="searchForm"]/select[2]/option')
        # 第一个选项值为空，故从2开始随机
        orderType = driver.find_element_by_xpath(
            '//form[@id="searchForm"]/select[2]/option[' + str(ranNo(2, orderTypeSelect.__len__())) + ']')
        orderTypeText = orderType.text
        orderType.click()
        driver.find_element_by_id('btnSubmit').click()
        driver.implicitly_wait(10)

        rsCount = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr')
        for i in range(1, rsCount.__len__() + 1):
            rsOrderType = driver.find_element_by_xpath(
                '//table[@id="contentTable"]/tbody/tr[' + str(i) + ']/td[3]/span')
            self.assertEquals(orderTypeText, rsOrderType.text)
        pageNo = int(driver.find_elements_by_xpath('/html/body/div/div/div/ul/li/a')[-2].text)

        # 对每一页的每一列进行检查
        if pageNo > 1:
            for i in range(2, pageNo + 1):
                driver.find_element_by_link_text(str(i)).click()
                driver.implicitly_wait(10)
                rsCount = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr').__len__() + 1
                for n in range(1, rsCount):
                    rsProductNo = driver.find_element_by_xpath(
                        '//table[@id="contentTable"]/tbody/tr[' + str(n) + ']/td[3]/span')
                    self.assertEquals(orderTypeText, rsProductNo.text)


if __name__ == '__main__':
    unittest.main()