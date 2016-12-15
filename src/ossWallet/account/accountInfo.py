# coding=utf-8
import unittest
from selenium.webdriver import ActionChains
from db.ora.oradao import Oradao
from util.datview import getNum
from util.initialize import Initialize

__author__ = 'Regend'


# 电子钱包账户管理
class AccountInfo(unittest.TestCase):
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

    def testAccount(self):
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
        driver.find_element_by_xpath('//li[@id="left_menu_77"]/a/span').click()
        chain.move_to_element(menu).perform()

        driver.implicitly_wait(10)
        # 切换至iframe
        driver.switch_to_frame('contentIframe77')

        # 测试数据总数是否一致
        sqlCount = 'select * from wm_account_info where company_code = \'' + conf.state + '\''
        sqlNum = Oradao.sqlCount(Oradao(), str(sqlCount))
        pageBottom = driver.find_elements_by_xpath('/html/body/div/div/ul/li')
        accountNum = getNum(str(pageBottom[pageBottom.__len__()-2].text))
        self.assertEquals(str(sqlNum), accountNum)

        # 获取第一条数据各个字段值
        rsNo = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td[1]/a').text.strip(' ')
        rsMemberCode = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td[2]').text.strip(' ')
        rsName = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td[3]').text.strip(' ')
        rsPhone = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td[4]').text.strip(' ')
        rsCardType = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td[5]').text.strip(' ')
        rsCardNo = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td[6]').text.strip(' ')
        rsLastVistTime = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td[7]').text.strip(' ')
        rsRemark = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td[8]').text.strip(' ')

        # 根据账号ID从数据库中查出该记录其他信息
        accountSql = 'select * from wm_account_info  where  company_code = \'' \
                     + conf.state + '\' and account = \'' + rsNo + '\''
        accountInfo = Oradao.sqlDiy(Oradao(), str(accountSql))
        accountMemberCode = accountInfo['MEMBER_CODE'][0]
        accountName = accountInfo['NAME'][0]
        accountPhone = accountInfo['BIND_PHONE'][0]
        # 证件类型写死，0对应身份证，1对应护照
        accountCardType = accountInfo['CARD_TYPE'][0]
        if accountCardType == 0:
            accountCardType = u'身份证';
        elif accountCardType == 1:
            accountCardType = u'护照'
        accountCardNo = accountInfo['ID_CARD'][0]
        accountLastVistTime = accountInfo['LAST_VISIT_TIME'][0]
        accountRemark = accountInfo['REMARKS'][0]
        accountId = accountInfo['ID'][0]

        # 数据库查询结果和页面结果对比断言
        self.assertEquals(rsMemberCode, accountMemberCode)
        self.assert_(rsMemberCode, accountMemberCode)
        self.assertEquals(rsName, accountName)
        self.assertEquals(rsPhone, accountPhone)
        self.assertEquals(rsCardType, accountCardType)
        self.assertEquals(rsCardNo, accountCardNo)
        self.assertEquals(rsLastVistTime, accountLastVistTime)
        self.assertEquals(rsRemark, accountRemark)

        # 查询余额
        driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td[9]/a[3]').click()

        financeSql = 'select * from wm_finance_info where account_info_id = \'' + str(accountId) + '\''
        financeInfo = Oradao.sqlDiy(Oradao(), str(financeSql))
        financeCash = financeInfo['TOTAL_EWALLET_VALUE'][0]  # 电子货币
        financePoint = financeInfo['TOTAL_EWALLET_VALUE'][1]  # 旅游积分
        financeBonus = financeInfo['TOTAL_EWALLET_VALUE'][2]  # 奖金

        driver.implicitly_wait(10)
        rsCash = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[1]/td[2]').text
        rsPoint = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[2]/td[2]').text
        rsBonus = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr[3]/td[2]').text

        # 对比余额断言
        self.assertEquals("%.2f" % float(financeCash), "%.2f" % float(rsCash))
        self.assertEquals("%.2f" % float(financePoint), "%.2f" % float(rsPoint))
        self.assertEquals("%.2f" % float(financeBonus), "%.2f" % float(rsBonus))

if __name__ == '__main__':
    unittest.main()