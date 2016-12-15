# coding=utf-8
import unittest
from selenium.webdriver import ActionChains
from db.ora.oradao import Oradao
from util.initialize import Initialize
from util.ranchar import ranNo, ranFloat

__author__ = 'Regend'


# 税率策略
class ProductSaleTax(unittest.TestCase):
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
        driver.find_element_by_xpath('//li[@id="left_menu_7264"]/a/span').click()
        chain.move_to_element(menu).perform()

        driver.implicitly_wait(10)
        # 切换至iframe
        driver.switch_to_frame('contentIframe7264')

        # 查出数据库中的税率数据
        taxsql = """SELECT pst.*
          FROM pm_product_sale_tax pst, sys_area sa
          WHERE sa.parent_id = (
          SELECT id
          FROM sys_area
          WHERE code = '""" + conf.state + """'
          AND TYPE = 20)
          AND tax_Strategy = 'tax0'
          AND pst.area_id = sa.id"""
        saleTax = Oradao.sqlDiy(Oradao(), taxsql)
        tax = saleTax['TAX']
        # 获取税率的个数
        totalNum = driver.find_elements_by_class_name('easyui-panel')
        rsTax = []
        for i in range(totalNum.__len__()):
            rsTax.append(driver.find_element_by_id('tax_panel_' + str(i)).get_attribute('value'))
        tax = list(set(tax))
        for i in range(tax.__len__()):
            self.assertIn(str(tax[i]), rsTax)

        # 添加税率
        driver.find_element_by_id('addAddress').click()
        driver.implicitly_wait(10)
        # 输入0到1随机小数税率
        driver.find_element_by_xpath('//form[@id="inputForm"]/span[2]/input[1]').send_keys(str(ranFloat(0, 1, 1)))
        # 随机选择一个地区
        areas = driver.find_elements_by_class_name('isoffline')
        if areas.__len__() > 0:
            rsArea = areas[ranNo(0, areas.__len__() - 1)]
            rsAreaName = rsArea.text
            rsArea.click()
            driver.find_element_by_id('btnSubmits').click()

            # 检查是否添加成功
            driver.implicitly_wait(10)
            # 把关闭按钮的x和换行符过滤掉
            message = driver.find_element_by_id('messageBox').text.replace(u'×', '').strip('\n')
            self.assertEquals(message, u'保存成功')
            # 检查新添加的地区是否在列表中,若有则删除
            driver.find_element_by_link_text(rsAreaName).click()
        else:
            driver.quit()


if __name__ == '__main__':
    unittest.main()