# coding=utf-8
import logging
import unittest
import time
from selenium.webdriver import ActionChains
from util.initialize import Initialize

__author__ = 'Regend'


class PersonWeeklyPfm(unittest.TestCase):
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

    def testPersonWeeklyPfm(self):
        driver = self.driver
        conf = self.conf
        conf.stateChange(driver)
        driver.implicitly_wait(10)

        # 选择运营支撑平台
        driver.find_element_by_id('topMenu_1100').click()
        # 指定元素：奖金管理
        button = driver.find_element_by_id('left_menu_1220')
        # 指定元素：菜单
        menu = driver.find_element_by_class_name('nav-header')
        second_button = driver.find_element_by_id('left_menu_7821')

        # 鼠标移动到会员管理上
        chain = ActionChains(driver)
        chain.move_to_element(button).perform()
        time.sleep(0.5)
        # 鼠标移动到业绩查询
        chain.move_to_element(second_button).perform()
        driver.implicitly_wait(10)
        # 指定元素：会员信息维护，并点击操作
        driver.find_element_by_xpath('//li[@id="left_menu_7822"]/a/span').click()
        # 移开鼠标
        chain.move_to_element(menu).perform()
        time.sleep(1)
        # 切换至iframe
        driver.switch_to_frame('contentIframe7822')

        # 判断当前页面中是否有当前机构的数据
        self.assertIn(conf.state, driver.page_source)

if __name__ == '__main__':
    unittest.main()
