# coding=utf-8

import time
import unittest
from selenium.webdriver import ActionChains
from db.ora.oradao import Oradao
from util.initialize import Initialize
from util.ranchar import ranNo


__author__ = 'Maggie'


class PlacementChange(unittest.TestCase):

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

    def testPlacementChange(self):
        driver = self.driver
        conf = self.conf
        conf.stateChange(driver)
        driver.implicitly_wait(10)

        # 读取配置文件-取state值
        conf = Initialize()
        state = conf.state

        # MM008 安置组织调整-添加&审核
        # 选择运营支撑平台
        driver.find_element_by_id('topMenu_1100').click()
        # 指定元素：会员管理
        button = driver.find_element_by_id('left_menu_1210')
        # 指定元素：菜单
        menu = driver.find_element_by_class_name('nav-header')

        # 鼠标移动到会员管理上
        chain = ActionChains(driver)
        chain.move_to_element(button).perform()
        # 指定元素：安置网络调整，并点击操作
        driver.find_element_by_xpath('//li[@id="left_menu_2503"]/a/span').click()
        # 移开鼠标
        chain.move_to_element(menu).perform()
        time.sleep(1)
        # 切换至iframe
        driver.switch_to_frame('contentIframe2503')

        # 点击添加
        driver.find_element_by_id('btnAdd').click()
        driver.implicitly_wait(10)

        # 从数据库随机取出可用的会员编号和新安置人(当取不到值报错时，需先新增会员)
        member = Oradao.sqlDiy(Oradao(), 'select a.member_no,b.member_no as newPlacement_No,a.create_date from mm_member a,mm_member b where a.sponsor_id = b.id and a.sponsor_id is not null and a.company_code=\''+state+'\' and b.company_code=\''+state+'\' and to_char(a.create_date,\'yyyy-mm-dd\')>to_char(sysdate-3,\'yyyy-mm-dd\') and a.sponsor_id not in (select m.placement_id from mm_member m where m.placement_id is not null group by m.placement_id having count(m.placement_id)>= 5) order by a.create_date desc')
        num = ranNo(0, member['MEMBER_NO'].__len__()-1)
        member_no = member['MEMBER_NO'][num]
        newPlacement_no = member['NEWPLACEMENT_NO'][num]

        # 在页面输入取到的数据
        driver.find_element_by_id('memberNo').send_keys(member_no)
        driver.find_element_by_name('parentNo').send_keys(newPlacement_no)

        # 点击保存
        driver.find_element_by_id('btnSubmit').click()
        time.sleep(2)

        # 按会员编号查询
        driver.find_element_by_name('sp_member.memberNo_LIKE').send_keys(member_no)
        driver.find_element_by_id('btnSubmit').click()
        driver.implicitly_wait(10)

        # 统计查到多少条记录
        count = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr').__len__()

        # 从数据库取最新那条数据的创建时间
        placement_change = Oradao.sqlDiy(Oradao(), 'select p.create_date,m.member_no,p.placement_id,p.status from mm_placement_ref_change p,mm_member m where p.member_id=m.id and m.member_no=\''+member_no+'\' order by p.create_date desc')
        createDate = placement_change['CREATE_DATE'][0].strftime('%Y-%m-%d %H:%M:%S')

        # 循环取出各记录的创建时间，与数据库最新的对比，得到最新那条记录
        for i in range(1, count+1):
            asCreateDate = driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr['+str(i)+']/td[5]').text
            # 先把创建时间后的空格过滤
            if asCreateDate.strip(' ') == createDate:
                break

        # 点击审核
        driver.find_element_by_xpath('//table[@id="contentTable"]/tbody/tr['+str(i)+']/td[9]/a[1]').click()
        time.sleep(2)

        # 选择通过 或 不通过
        check_num = ranNo(1, 2)
        driver.find_element_by_xpath('//form[@id="inputForm"]/div[6]/div/input['+str(check_num)+']').click()
        time.sleep(2)

        # 点击保存
        driver.find_element_by_id('btnSubmit').click()
        time.sleep(2)

        # 审核后核对数据库该审核状态
        status = Oradao.sqlDiy(Oradao(), 'select p.create_date,m.member_no,p.placement_id,p.status from mm_placement_ref_change p,mm_member m where p.member_id=m.id and m.member_no=\''+member_no+'\' order by p.create_date desc')
        if check_num == 1:
            self.assertEqual(int(status['STATUS'][0]), 1)
        else:
            self.assertEqual(int(status['STATUS'][0]), 0)

if __name__ =='__main__':
    unittest.main()





