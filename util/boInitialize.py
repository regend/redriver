# coding=utf-8
from selenium.webdriver import ActionChains
import time
from db.ora.oradao import Oradao
from util.initialize import Initialize
from util.ranchar import ranNo

__author__ = 'Maggie'


class BoInitialize(Initialize):
    # 初始化member转换为dict
    def __init__(self, type=None):
        member_sql = '''
            SELECT mm.*
            FROM mm_member mm, sys_base_user sbu, sys_user_role sur
            WHERE mm.company_code = '%s'
            AND mm.enrollment_grade is not null
            AND mm.MEMBER_NO = sbu.LOGIN_NAME
            AND sbu.ID = sur.BASE_USER_ID
            AND sur.ROLE_ID in (7564,2154842,1658282)
        '''
        # 取能下重消单的会员
        if type == 1:
            member_sql = member_sql + 'and mm.enrollment_grade != 0'

        member_db = Oradao().sqlDiy(member_sql % self.state)
        num = 0
        self.member = {}
        if member_db['ID'].__len__() > 0:
            num = ranNo(0, member_db['ID'].__len__() - 1)
        for i in member_db.items():
            self.member.setdefault(i[0], i[1][num])

    # backoffice 登录
    def login(self):
        # oss登录
        driver = self.start()
        self.stateChange(driver)
        driver.implicitly_wait(10)

        # 打开oss会员信息维护页面
        # 选择运营支撑平台
        driver.find_element_by_id('topMenu_1100').click()
        # 会员管理
        button = driver.find_element_by_id('left_menu_1210')
        # 菜单
        menu = driver.find_element_by_class_name('nav-header')

        # 鼠标移动到会员管理上
        chain = ActionChains(driver)
        chain.move_to_element(button).perform()
        driver.implicitly_wait(10)
        # 会员信息维护，并点击操作
        driver.find_element_by_xpath('//li[@id="left_menu_1211"]/a/span').click()
        # 移开鼠标
        chain.move_to_element(menu).perform()
        driver.implicitly_wait(10)
        # 切换至iframe
        driver.switch_to_frame('contentIframe1211')

        # 会员信息维护，随机选一个会员，点击登录
        memberNo = self.member['MEMBER_NO']
        driver.find_element_by_name('sp_memberNo_ILIKE').send_keys(memberNo)
        driver.find_element_by_id('btnSubmit').click()
        time.sleep(2)

        # 切换到backoffice窗口
        # 点击登录按钮打开新窗口
        driver.find_element_by_xpath('//table[@id="treeTable1"]/tbody/tr/td[12]/a[1]').click()
        time.sleep(2)
        # 遍历所有窗口的句柄
        for handle in driver.window_handles:
            # 切换到最后打开的窗口
            driver.switch_to_window(handle)
        self.boLangChange(driver, 'zh_CN')
        return driver

    # backoffice 切换语言
    @staticmethod
    def boLangChange(driver, lang):
        driver.implicitly_wait(10)
        element = driver.find_element_by_id('locale')
        element.find_element_by_xpath('//option[@value="' + lang + '"]').click()
        driver.implicitly_wait(10)
