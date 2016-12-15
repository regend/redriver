# coding=utf-8

import time
import unittest
from selenium.webdriver import ActionChains
from db.ora.oradao import Oradao
from util.datview import transData
from util.initialize import Initialize

from util.ranchar import ranNo


__author__ = 'Maggie'


class MemberInfo(unittest.TestCase):
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

    def testMember(self):
        driver = self.driver
        conf = self.conf
        state = conf.state
        conf.stateChange(driver)
        driver.implicitly_wait(10)

        # MM001 会员信息维护-查询

        # 选择运营支撑平台
        driver.find_element_by_id('topMenu_1100').click()
        # 指定元素：会员管理
        button = driver.find_element_by_id('left_menu_1210')
        # 指定元素：菜单
        menu = driver.find_element_by_class_name('nav-header')

        # 鼠标移动到会员管理上
        chain = ActionChains(driver)
        chain.move_to_element(button).perform()
        driver.implicitly_wait(10)
        # 指定元素：会员信息维护，并点击操作
        driver.find_element_by_xpath('//li[@id="left_menu_1211"]/a/span').click()
        # 移开鼠标
        chain.move_to_element(menu).perform()
        time.sleep(1)
        # 切换至iframe
        driver.switch_to_frame('contentIframe1211')

        # 按会员编码查询

        # 从数据库查询会员编号
        Member = Oradao.sqlDiy(Oradao(),
                               'select * from (select * from MM_MEMBER m where m.company_code=\'' + state + '\' order by m.create_date desc) where rownum<=10')

        # 随机取会员编号
        num = ranNo(0, Member['ID'].__len__() - 1)
        memberNo = Member['MEMBER_NO'][num]
        sponsorId = Member['SPONSOR_ID'][num]
        placementId = Member['PLACEMENT_ID'][num]

        # 页面查询
        if not driver.find_element_by_id('btnAdd').is_displayed():
            driver.find_element_by_class_name('open-close').click()
        time.sleep(0.5)
        driver.find_element_by_name('sp_memberNo_ILIKE').send_keys(memberNo)
        driver.find_element_by_id('btnSubmit').click()

        # 页面刷新元素变化了，需要加这个，否则后面元素会获取不到
        time.sleep(2)

        # 获取列表各字段数据
        rsXpath = driver.find_elements_by_xpath('//table[@id="treeTable1"]/tbody/tr/td')
        rsMemberNo = rsXpath[1].text
        rsMemberName = rsXpath[2].text
        rsMemberGrade = rsXpath[3].text
        rsCreater = rsXpath[4].text
        rsCreateDate = rsXpath[5].text
        rsCreateTime = rsXpath[6].text
        rsSponsor = rsXpath[7].text
        rsPlacement = rsXpath[8].text
        rsSubType = rsXpath[9].text

        # 断言
        self.assertEquals(rsMemberNo, memberNo)
        self.assertEqual(rsMemberName, Member['NAME'][num])
        self.assertEqual(rsMemberGrade, transData('member.enrollmentGrade').get(Member['ENROLLMENT_GRADE'][num]))
        self.assertEqual(rsCreater, Member['CREATE_BY'][num])
        self.assertEqual(rsCreateDate, Member['CREATE_DATE'][num].strftime('%Y-%m-%d'))
        self.assertEqual(rsCreateTime, Member['CREATE_DATE'][num].strftime('%H:%M:%S'))
        # 推荐人&安置人编号
        sponsorNo = Oradao.sqlDiy(Oradao(), 'select * from MM_MEMBER m where m.id=' + str(sponsorId))['MEMBER_NO'][0]
        placementNo = Oradao.sqlDiy(Oradao(), 'select * from MM_MEMBER m where m.id=' + str(placementId))['MEMBER_NO'][
            0]
        self.assertEqual(rsSponsor, sponsorNo)
        self.assertEqual(rsPlacement, placementNo)
        self.assertEqual(rsSubType, transData('member.subtype').get(Member['SUBTYPE'][num]))


if __name__ == '__main__':
    unittest.main()





