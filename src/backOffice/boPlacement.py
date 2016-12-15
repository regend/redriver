# coding=utf-8

import unittest
import time
from db.ora.oradao import Oradao
from util.boInitialize import BoInitialize
from util.datview import transData

__author__ = 'Maggie'


class BoPlacement(unittest.TestCase):
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

    def testBoPlacement(self):
        driver = self.driver
        conf = self.conf
        # 切换语言
        conf.boLangChange(driver, 'zh_CN')
        # 声明member对象
        member = conf.member

        time.sleep(5)

        # 打开我的业务-安置网
        driver.find_element_by_xpath('//ul[@id="mainmenu"]/li[2]/a').click()
        driver.find_element_by_id('8077').click()

        # 当前会员ID
        member_id = member['ID']

        # 从页面获取该会员的各明细信息
        member_no = driver.find_element_by_id('memberDetail_'+str(member_id)).get_attribute('memberno')
        member_status = driver.find_element_by_id('memberDetail_'+str(member_id)).get_attribute('memberstatustext')
        member_son = driver.find_element_by_id('memberDetail_'+str(member_id)).get_attribute('memberson')
        member_grade = driver.find_element_by_id('memberDetail_'+str(member_id)).get_attribute('membergradetext')
        order_date = driver.find_element_by_id('memberDetail_'+str(member_id)).get_attribute('firstorderbonusdate')
        member_name = driver.find_element_by_id('memberDetail_'+str(member_id)).get_attribute('membername')
        member_sponsorno = driver.find_element_by_id('memberDetail_'+str(member_id)).get_attribute('membersponsorno')

        # 断言明细信息
        self.assertEqual(member_no, member['MEMBER_NO'])
        self.assertEqual(member_status, transData('member.status').get(member['STATUS']))
        self.assertEqual(member_name, member['NAME'][0:19])
        if order_date == '':
            self.assertEqual(order_date, member['JOIN_DATE'])
        else:
            self.assertEqual(order_date, member['JOIN_DATE'].strftime('%Y-%m-%d'))
        sponsor_no = Oradao.sqlDiy(Oradao(),
                                  'select * from mm_member m where m.id=(select m.sponsor_id from mm_member m where m.member_no=\''+member['MEMBER_NO']+'\')')
        self.assertEqual(member_sponsorno, sponsor_no['MEMBER_NO'][0])
        self.assertEqual(member_grade, transData('member.enrollmentGrade').get(member['ENROLLMENT_GRADE']))

        # 判断当前会员是否有安置下线,有则对下线编号进行断言
        if member_son > '0':
            # 数据库取安置下线
            son_no = Oradao.sqlDiy(Oradao(),
                                     'select * from mm_member m where m.placement_id=(select m.id from mm_member m where m.member_no=\''+member['MEMBER_NO']+'\') order by m.member_no asc')
            num = son_no['ID'].__len__()
            # 循环取下线编号进行断言
            for i in range(0, num):
                member_sonId = son_no['ID'][i]
                member_sonNo = driver.find_element_by_id('memberDetail_'+str(member_sonId)).get_attribute('memberno')
                self.assertEqual(member_sonNo, son_no['MEMBER_NO'][i])

if __name__ == '__main__':
    unittest.main()





