# coding=utf-8

import unittest
import time
from db.ora.oradao import Oradao
from util.boInitialize import BoInitialize
from util.ranchar import ranNo

__author__ = 'Maggie'


class BoPlacementSet(unittest.TestCase):
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

    # 自动安置功能
    def testBoPlacementSet(self):
        driver = self.driver
        conf = self.conf
        # 切换语言
        conf.boLangChange(driver, 'zh_CN')
        driver.implicitly_wait(5)

        num = ranNo(0, 2)
        if num != 0:
            # 打开我的账户-设置
            driver.find_element_by_xpath('//ul[@id="mainmenu"]/li[5]/a').click()
            time.sleep(2)
            driver.find_element_by_id('8100').click()
            driver.implicitly_wait(5)

            # 修改密码
            driver.execute_script('scrollTo(0,1000)')
            driver.find_element_by_id('emailId').clear()
            driver.find_element_by_id('emailId').send_keys('test@163.com')
            driver.find_element_by_id('passwordId').send_keys('123456')
            driver.find_element_by_id('confirmNewPasswordId').send_keys('123456')
            driver.find_element_by_xpath('//div[@id="tab_1_1"]/div[3]/div/div/button[1]').click()
            time.sleep(2)

            # 关闭提示弹框
            driver.switch_to_alert().accept()
            time.sleep(2)

            # 退出重新登录
            # driver.find_element_by_class_name('username-hide-mobile').click()
            if conf.env == 'sandbox':
                driver.get('https://sandbox-d-v1.jmtop.com/backOffice/logout')
            elif conf.env == 'production':
                driver.get('https://dist.jmtop.com/backOffice/logout')
            driver.implicitly_wait(10)
            driver.find_element_by_id('password').send_keys('123456')
            time.sleep(2)

            driver.find_element_by_id('btnLogin').click()
            driver.implicitly_wait(5)

        # 打开我的业务-安置网系谱
        driver.find_element_by_xpath('//ul[@id="mainmenu"]/li[2]').click()
        driver.implicitly_wait(10)
        driver.find_element_by_id('8078').click()
        time.sleep(2)

        # 点击安置设置
        driver.find_element_by_id('placementSettingBtn').click()
        time.sleep(2)

        # 随机设置
        driver.find_elements_by_id('placementSetting')[num].click()
        time.sleep(2)

        # 点击保存
        driver.find_element_by_id('placementSettingFormBtn').click()
        driver.implicitly_wait(5)

        # 输入登录密码
        if num != 0:
            driver.find_element_by_id('first-time-psw').send_keys('123456')
            driver.find_element_by_id('placementSettingAgreeBtn').click()
            driver.implicitly_wait(5)
            driver.find_element_by_id('second-time-psw').send_keys('123456')
            driver.find_element_by_id('placementSettingRepeatOK').click()
            driver.implicitly_wait(5)

        # 当前登录的会员
        member = conf.member
        member_id = member['ID']

        # 断言
        value = Oradao.sqlDiy(Oradao(), 'select * from MM_MEMBER_CHANGE c where c.member_id=' + str(member_id) + 'and c.operate_type=50 order by c.create_date desc')['NEW_VALUE'][0]
        self.assertEqual(num, int(value))

if __name__ == '__main__':
    unittest.main()





