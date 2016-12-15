# coding=utf-8
import time
import unittest
from selenium.webdriver import ActionChains
from db.ora.oradao import Oradao
from util.initialize import Initialize

from util.ranchar import ranEN, ranNo


__author__ = 'Maggie'


class MemberAdd(unittest.TestCase):
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

    def testMemberAdd(self):
        driver = self.driver
        conf = self.conf
        state = conf.state
        conf.stateChange(driver)
        driver.implicitly_wait(10)

        # MM002 添加会员

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
        chain.move_to_element(menu).perform()
        time.sleep(1)
        # 切换至iframe
        driver.switch_to_frame('contentIframe1211')

        # 添加会员
        if not driver.find_element_by_id('btnAdd').is_displayed():
            driver.find_element_by_class_name('open-close').click()
        time.sleep(0.5)
        driver.find_element_by_id('btnAdd').click()
        driver.implicitly_wait(10)

        # 输入会员名称
        member_name = ranEN(8)
        time.sleep(2)
        driver.find_element_by_name('name').send_keys(member_name)

        # 从数据库查推荐人&安置人编号（取最新一条）
        member = Oradao.sqlDiy(Oradao(), 'select * from MM_MEMBER m where m.company_code=\''+state+'\' order by m.create_date desc')
        member_no = member['MEMBER_NO'][0]
        member_id = member['ID'][0]
        driver.find_element_by_name('sponsorMemberNo').send_keys(member_no)

        # 判断是否自动安置
        Placement = Oradao.sqlDiy(Oradao(), 'select * from MM_MEMBER_CHANGE c where c.member_id=' + str(member_id) + 'and c.operate_type=50 order by c.create_date desc')
        len = Placement['ID'].__len__()
        if len == 0:
            value = 0
        else:
            value = Placement['NEW_VALUE'][0]
        if value == 0:
            driver.find_element_by_name('placementMemberNo').send_keys(member_no)

        # 输入身份证
        if state == 'US':
            identification = str(ranNo(100000000, 999999999))
        else:
            identification = str(ranNo(400000000000000000, 999999999999999999))
        driver.find_element_by_id('sinTaxId').send_keys(identification)

        # 输入移动电话
        mobilePhone = str(ranNo(13500000000, 13799999999))
        driver.find_element_by_id('mobilePhone').send_keys(mobilePhone)

        # 保存
        driver.switch_to_default_content()
        driver.execute_script('scrollTo(0,500)')
        driver.switch_to_frame('contentIframe1211')
        driver.find_element_by_id('btnSubmit').click()
        driver.implicitly_wait(20)

        # 依次 点击 2个 返回
        driver.switch_to_default_content()
        driver.execute_script('scrollTo(0,0)')
        driver.switch_to_frame('contentIframe1211')
        driver.find_element_by_xpath('//form[@id="inputForm"]/div[1]/div[3]/input[12]').click()

        driver.switch_to_default_content()
        driver.execute_script('scrollTo(0,500)')
        driver.switch_to_frame('contentIframe1211')
        driver.find_element_by_xpath('//div[@id="showSaveDiv"]/div/input[5]').click()

        driver.switch_to_default_content()
        driver.execute_script('scrollTo(0,0)')
        driver.switch_to_frame('contentIframe1211')

        # 新增会员断言
        memberNew = Oradao.sqlDiy(Oradao(), 'select * from MM_MEMBER m where m.company_code=\''+state+'\' order by m.create_date desc')
        memberNo = memberNew['MEMBER_NO'][0]
        if not driver.find_element_by_id('btnAdd').is_displayed():
            driver.find_element_by_class_name('open-close').click()
        time.sleep(0.5)
        driver.find_element_by_name('sp_memberNo_ILIKE').send_keys(memberNo)
        driver.find_element_by_id('btnSubmit').click()
        time.sleep(2)

        # 获取列表会员编号
        rsMemberNo = driver.find_elements_by_xpath('//table[@id="treeTable1"]/tbody/tr/td[2]')[0].text
        self.assertEquals(rsMemberNo, memberNo)

if __name__ == '__main__':
    unittest.main()





