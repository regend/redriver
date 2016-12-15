# coding=utf-8

import time
import unittest
from selenium.webdriver import ActionChains
from db.ora.oradao import Oradao
from util.initialize import Initialize
from util.ranchar import ranNo


__author__ = 'Maggie'


class PlacementSelect(unittest.TestCase):
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

    def testplacementSelect(self):
        driver = self.driver
        conf = self.conf
        conf.stateChange(driver)
        driver.implicitly_wait(10)

        # MM005 安置组织-向下查询

        # 选择运营支撑平台
        driver.find_element_by_id('topMenu_1100').click()
        # 指定元素：会员管理
        button = driver.find_element_by_id('left_menu_1210')
        # 指定元素：菜单
        menu = driver.find_element_by_class_name('nav-header')

        # 鼠标移动到会员管理上
        chain = ActionChains(driver)
        chain.move_to_element(button).perform()
        # 指定元素：安置组织查询，并点击操作
        driver.find_element_by_xpath('//li[@id="left_menu_1217"]/a/span').click()
        # 移开鼠标
        chain.move_to_element(menu).perform()
        time.sleep(1)
        # 切换至iframe
        driver.switch_to_frame('contentIframe1217')

        # 从数据库随机取会员编号
        member = Oradao.sqlDiy(Oradao(),
                               'select * from (select * from mm_member m where m.company_code=\'' + conf.state + '\' order by m.create_date desc) where rownum <=100')
        num = ranNo(0, member['ID'].__len__() - 1)
        member_no = member['MEMBER_NO'][num]
        member_id = member['ID'][num]

        # 输入会员编号，进行查询
        driver.find_element_by_name('memberNo').send_keys(member_no)
        driver.find_element_by_id('btnSubmit').click()
        driver.implicitly_wait(10)

        # 从数据库查该安置人的直接下级会员编号和ID
        dMember = Oradao.sqlDiy(Oradao(), 'select * from mm_member m where m.placement_id=' + str(
            member_id) + 'order by m.create_date')
        # 统计直接下级会员数
        dNum = dMember['ID'].__len__()

        # 循环取值进行断言(从页面获取会员编号并截取)
        for i in range(0, dNum):
            dMember_no = driver.find_element_by_xpath('//tr[@id="' + str(dMember['ID'][i]) + '"]/td[1]/span[4]').text
            dMemberNo = dMember_no[0:10]
            self.assertEquals(dMemberNo, dMember['MEMBER_NO'][i])


if __name__ == '__main__':
    unittest.main()





