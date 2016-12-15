# coding=utf-8
import unittest
import time
from util.boInitialize import BoInitialize
from util.datview import *

__author__ = 'Maggie'


class BoIndex(unittest.TestCase):
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

    def testBoIndex(self):
        driver = self.driver
        conf = self.conf
        member = conf.member

        driver.implicitly_wait(10)
        # 分别获取页面中注册级别0，当前奖衔1，历史最高奖衔2
        topmsg = driver.find_elements_by_class_name('number')
        self.assertEquals(transData('member.enrollmentGrade').get(member['ENROLLMENT_GRADE']),
                          topmsg[0].text.strip(' '))
        # self.assertEquals(transData('member.enrollmentGrade').get(member['ENROLLMENT_GRADE']),
        # topmsg[1].text.strip(' '))
        # 若数据库中最高奖衔字段值为空，则不去查对应的值进行断言
        if member['PIN_TITLE'] is '':
            self.assertEquals('', topmsg[2].text.strip(' '))
        else:
            self.assertEquals(transData('awardsInf.awards').get(member['PIN_TITLE']),
                              topmsg[2].text.strip(' '))

        # 测试当前工作周
        cur_week = get_cur_week()
        last_week = get_last_stage(cur_week)
        page_working_stage = driver.find_element_by_xpath('//tbody[@class="font-blue-chambray"]/tr[1]/td[1]').text
        self.assertEquals(page_working_stage, cur_week)

        # 查询会员本月及上月业绩
        total_bv = driver.find_elements_by_xpath('//span[@title="总业绩"]')
        # 上月总业绩
        page_last_bv = total_bv[0].text.replace(',', '')
        # 本月总业绩
        page_cur_bv = total_bv[1].text.replace(',', '')
        pfm_sql = '''
            SELECT *
            FROM br_Person_monthly_pfm
            WHERE working_Stage = '%s'
            AND member_id = '%s'
            '''
        cur_pfm = Oradao().sqlDiy(pfm_sql % (cur_week[:-2], member['ID']))
        last_pfm = Oradao().sqlDiy(pfm_sql % (last_week, member['ID']))
        # 若数据库中没记录，则当月业绩为0
        if cur_pfm['ID'].__len__() == 0:
            cur_pfm_bv = 0
        else:
            cur_pfm_bv = cur_pfm['FIRST_PURCHASE_BV'][0] + cur_pfm['UPGRADE_BV'][0] + cur_pfm['REPEAT_PURCHASE_BV'][0]
        self.assertEquals("%.0f" % float(page_cur_bv), str(cur_pfm_bv))
        if last_pfm['ID'].__len__() == 0:
            last_pfm_bv = 0
        else:
            last_pfm_bv = last_pfm['FIRST_PURCHASE_BV'][0] + last_pfm['UPGRADE_BV'][0] + last_pfm['REPEAT_PURCHASE_BV'][
                0]
        self.assertEquals("%.0f" % float(page_last_bv), str(last_pfm_bv))

        # 启动奖金，组织奖金
        web_bonus_bv = driver.find_elements_by_xpath('//div[@class="portlet-body"]')[2].find_elements_by_class_name(
            'uppercase')
        web_start_bonus_bv = web_bonus_bv[0].text.strip(' BV').replace(',', '')
        web_organizational_bonus_bv = web_bonus_bv[3].text.strip(' BV').replace(',', '')
        bonus_sql = '''
          SELECT *
          FROM BM_WEEKLY_BONUS_DAILY
          WHERE WORKING_STAGE = '%s'
          AND member_id = '%s'
          '''
        cur_bouns = Oradao().sqlDiy(bonus_sql % (cur_week, member['ID']))
        # 若数据库中没记录，则奖金为0
        if cur_bouns['ID'].__len__() == 0:
            start_bonus_bv = 0
            organizational_bonus_bv = 0
        else:
            start_bonus_bv = cur_bouns['START_BONUS_BV'][0]
            organizational_bonus_bv = cur_bouns['ORGANIZATIONAL_BONUS_BV'][0]
        self.assertEquals("%.0f" % float(web_start_bonus_bv), str(start_bonus_bv))
        self.assertEquals("%.0f" % float(getNum(web_organizational_bonus_bv)), str(organizational_bonus_bv))

        # 假期积分
        hld_inter = driver.find_elements_by_xpath('//div[@class="portlet-body"]')[3].find_elements_by_class_name(
            'uppercase')
        web_hld_inter = hld_inter[0].text
        web_hld_inter_total = hld_inter[1].text
        web_account2 = hld_inter[2].text
        hld_sql = '''
          SELECT *
          FROM BM_MONTHLY_BONUS_DAILY
          WHERE WORKING_STAGE = '%s'
          AND member_id = '%s'
          '''
        hld_db_inter_ = Oradao().sqlDiy(hld_sql % (cur_week[:-2], member['ID']))
        # 若数据库中没记录，则积分为0
        if hld_db_inter_['ID'].__len__() == 0:
            hld_inter = 0
            hld_inter_total = 0
        else:
            hld_inter = hld_db_inter_['HOLIDAY_INTEGRAL'][0]
            hld_inter_total = hld_db_inter_['HOLIDAY_INTEGRAL_TOTAL'][0]
        self.assertEquals("%.0f" % float(web_hld_inter), str(hld_inter))
        self.assertEquals("%.0f" % float(web_hld_inter_total), str(hld_inter_total))

        account2_sql = '''
            SELECT *
            FROM VACATION_POINT_ACCOUNT2
            WHERE flg = '%s'
            AND YEAR = '%s'
            AND member_id = '%s'
            '''
        account2_db = Oradao().sqlDiy(account2_sql % (0, time.localtime().tm_year - 1, member['ID']))
        # 若数据库中没记录，则积分为0
        if account2_db['ID'].__len__() == 0:
            account2_inter = 0
        else:
            account2_inter = account2_db['VPTS'][0]
        self.assertEquals("%.0f" % float(web_account2), str(account2_inter))

        # 测试公告栏
        announcement_sql = '''
            SELECT DISTINCT sa.id AS a,sa.*
            FROM sys_announcement sa inner join sys_announcement_office sao ON sa.id =
            sao.announcement_id inner join sys_office so ON sao.office_id =
            so.id
            AND ( so.del_flag = '0') inner join sys_announcement_image sai ON sa.id
            = sai.announcement_id
            WHERE sa.create_date < SYSDATE
            AND so.id = '%s'
            AND sa.del_flag = '0'
            AND (sa.publish_place = '0'
            OR sa.publish_place = '2')
            AND ROWNUM <= 5
            ORDER BY sa.id DESC
        '''
        announcement_db = Oradao().sqlDiy(announcement_sql % get_officeid_by_code(conf.state))
        web_announcement = driver.find_elements_by_xpath('//div[@id="myCarousel"]/div/div/img')
        if announcement_db['ID'].__len__() > 0:
            announcement_title = announcement_db['TITLE']
            for i in range(web_announcement.__len__()):
                self.assertEquals(web_announcement[i].get_attribute('alt'), announcement_title[i])
        else:
            self.assertEquals(web_announcement.__len__(), announcement_db['ID'].__len__())


if __name__ == '__main__':
    unittest.main()
