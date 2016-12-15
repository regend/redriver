# coding=utf-8
import unittest
from selenium.webdriver import ActionChains
from db.ora.oradao import Oradao
from util.initialize import Initialize

__author__ = 'Regend'


# 电子钱包充值查询
class FundIn(unittest.TestCase):
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

    def testFund(self):
        # 初始化登录
        driver = self.driver
        conf = self.conf
        conf.stateChange(driver)
        driver.implicitly_wait(10)

        # 选择运营支撑平台
        driver.find_element_by_id('topMenu_1100').click()
        button = driver.find_element_by_id('left_menu_73')
        menu = driver.find_element_by_class_name('nav-header')

        # 鼠标悬停在电子钱包上
        chain = ActionChains(driver)
        chain.move_to_element(button).perform()
        driver.find_element_by_xpath('//li[@id="left_menu_85"]/a/span').click()
        chain.move_to_element(menu).perform()

        driver.implicitly_wait(10)
        # 切换至iframe
        driver.switch_to_frame('contentIframe85')

        # 判断有多少条数据，若只有一条xpath的tr长度只有1
        driver.implicitly_wait(10)
        tolalnum = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr').__len__()
        # 取出唯一的一条数据，根据钱包账号查询对应的数据进行验证
        if tolalnum == 1:
            rsAccountNo = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr/td[1]').text.strip(' ')
            rsMemberNo = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr/td[2]').text.strip(' ')
            rsMemberName = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr/td[3]').text.strip(' ')
            rsEwalletType = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr/td[4]').text.strip(' ')
            rsEwalletValue = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr/td[5]').text.strip(' ')
            rsEwalletValueToltal = driver.find_element_by_xpath(
                '//table[@id="contentTable"]/tbody/tr/td[6]').text.strip(' ')
            rsSubmitName = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr/td[7]').text.strip(' ')
            rsSubmitTime = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr/td[8]').text.strip(' ')
            rsAuditName = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr/td[9]').text.strip(' ')
            rsAuditTime = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr/td[10]').text.strip(' ')
            rsAuditStatus = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr/td[11]').text.strip(' ')

            fundSql = 'select wbd.*, wfi.*, mm.name from wm_balance_detail wbd, wm_finance_info wfi, mm_member mm where ' \
                      'wfi.member_id = mm.id and wbd.FINANCE_INFO_ID = wfi.id and wbd.company_code = \'' + conf.state + \
                      '\' and wbd.origin = 30 and wfi.account = \'' + rsAccountNo + '\''
            fundIn = Oradao.sqlDiy(Oradao(), str(fundSql))
            memberNo = fundIn['MEMBER_CODE'][0]
            memberName = fundIn['NAME'][0]
            ewalletType = fundIn['EWALLET_TYPE'][0]
            if ewalletType == '1':
                ewalletType = u'电子货币'
            elif ewalletType == '2':
                ewalletType = u'旅游积分'
            elif ewalletType == '3':
                ewalletType = u'奖金'
            ewalletValue = fundIn['EWALLET_VALUE'][0]
            ewalletValueToltal = fundIn['EWALLET_VALUE_TOTAL'][0]
            submitName = fundIn['SUBMIT_ID'][0]
            if fundIn['SUBMIT_TIME'][0] != '':
                submitTime = fundIn['SUBMIT_TIME'][0].strftime('%Y-%m-%d %H:%M:%S')
            else:
                submitTime = ''
            auditName = fundIn['AUDITOR_ID'][0]
            if fundIn['AUDIT_TIME'][0] != '':
                auditTime = fundIn['AUDIT_TIME'][0].strftime('%Y-%m-%d %H:%M:%S')
            else:
                auditTime = ''
            status = fundIn['STATUS'][0]
            if status == 1:
                status = u'待审核'
            elif status == 2:
                status = u'通过'
            elif status == 3:
                status = u'不通过'

            self.assertEquals(memberNo, rsMemberNo)
            self.assertEquals(memberName, rsMemberName)
            self.assertEquals(ewalletType, rsEwalletType)
            self.assertEquals("%.2f" % float(ewalletValue), "%.2f" % float(rsEwalletValue))
            self.assertEquals("%.2f" % float(ewalletValueToltal), "%.2f" % float(rsEwalletValueToltal))
            self.assertEquals(submitName, rsSubmitName)
            self.assertEquals(submitTime, rsSubmitTime)
            self.assertEquals(auditName, rsAuditName)
            self.assertEquals(auditTime, rsAuditTime)
            self.assertEquals(status, rsAuditStatus)

        # 当数据量大于1时，tr值取第一条
        elif tolalnum > 1:
            rsAccountNo = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td[2]').text.strip(' ')
            rsMemberNo = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td[3]').text.strip(' ')
            rsMemberName = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td[4]').text.strip(' ')
            rsEwalletType = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td[5]').text.strip(
                ' ')
            rsEwalletValue = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td[6]').text.strip(
                ' ')
            rsEwalletValueToltal = driver.find_element_by_xpath(
                '//table[@id="contentTable"]/tbody/tr[1]/td[7]').text.strip(' ')
            rsSubmitName = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td[8]').text.strip(' ')
            rsSubmitTime = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td[9]').text.strip(' ')
            rsAuditName = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td[10]').text.strip(' ')
            rsAuditTime = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td[11]').text.strip(' ')
            rsAuditStatus = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td[12]').text.strip(
                ' ')

            fundSql = 'select wbd.*, wfi.*, mm.name from wm_balance_detail wbd, wm_finance_info wfi, mm_member mm where ' \
                      'wfi.member_id = mm.id and wbd.FINANCE_INFO_ID = wfi.id and wbd.company_code = \'' + conf.state + \
                      '\' and wbd.origin = 30 and wfi.account = \'' + rsAccountNo + '\' order by wbd.AUDIT_TIME desc, submit_time desc'
            fundIn = Oradao.sqlDiy(Oradao(), str(fundSql))
            memberNo = fundIn['MEMBER_CODE'][0]
            memberName = fundIn['NAME'][0]
            ewalletType = fundIn['EWALLET_TYPE'][0]
            if ewalletType == '1':
                ewalletType = u'电子货币'
            elif ewalletType == '2':
                ewalletType = u'旅游积分'
            elif ewalletType == '3':
                ewalletType = u'奖金'
            ewalletValue = fundIn['EWALLET_VALUE'][0]
            ewalletValueToltal = fundIn['EWALLET_VALUE_TOTAL'][0]
            submitName = fundIn['SUBMIT_ID'][0]
            if fundIn['SUBMIT_TIME'][0] != '':
                submitTime = fundIn['SUBMIT_TIME'][0].strftime('%Y-%m-%d %H:%M:%S')
            else:
                submitTime = ''
            auditName = fundIn['AUDITOR_ID'][0]
            if fundIn['AUDIT_TIME'][0] != '':
                auditTime = fundIn['AUDIT_TIME'][0].strftime('%Y-%m-%d %H:%M:%S')
            else:
                auditTime = ''
            status = fundIn['STATUS'][0]
            if status == 1:
                status = u'待审核'
            elif status == 2:
                status = u'通过'
            elif status == 3:
                status = u'不通过'

            self.assertEquals(memberNo, rsMemberNo)
            self.assertEquals(memberName, rsMemberName)
            self.assertEquals(ewalletType, rsEwalletType)
            self.assertEquals("%.2f" % float(ewalletValue), "%.2f" % float(rsEwalletValue))
            self.assertEquals("%.2f" % float(ewalletValueToltal), "%.2f" % float(rsEwalletValueToltal))
            self.assertEquals(submitName, rsSubmitName)
            self.assertEquals(submitTime, rsSubmitTime)
            self.assertEquals(auditName, rsAuditName)
            self.assertEquals(auditTime, rsAuditTime)
            self.assertEquals(status, rsAuditStatus)

        if tolalnum < 1:
            raise AssertionError(u'未知错误')

if __name__ == '__main__':
    unittest.main()