# coding=utf-8
import logging
import unittest
import time
from db.ora.oradao import Oradao
from util.actions import random_select_by_id
from util.boInitialize import BoInitialize
from util.ranchar import ranNo, ranEN

__author__ = 'Regend'


# 这脚本真是复杂
class BoRegister(unittest.TestCase):
    def setUp(self):
        self.conf = BoInitialize()
        self.driver = self.conf.login()
        self.verificationErrors = []
        pass

    def tearDown(self):
        self.conf.getScreenshot(self)
        self.assertEqual([], self.verificationErrors)
        logging.info(self.driver.page_source)
        self.driver.quit()
        pass

    def testBoRegister(self):
        driver = self.driver
        conf = self.conf
        member = conf.member

        # 切换语言
        conf.boLangChange(driver, 'zh_CN')

        driver.find_element_by_link_text('注册').click()
        driver.implicitly_wait(10)
        web_sponsor = driver.find_element_by_class_name('sponsor').text
        # 1.判断推荐人和当前用户是否一致
        self.assertEquals(member['NAME'], web_sponsor)

        driver.find_element_by_xpath('//div[@class="modal-footer"]/button[1]').click()
        time.sleep(2)
        # 2.选择国家
        company = driver.find_element_by_css_selector('a[companycode="' + conf.state + '"]')
        company.click()
        time.sleep(2)

        # 选择语言，排除掉选择不同国家选项
        lang = driver.find_elements_by_xpath(
            '//div[@id="myLangModal-' + company.get_attribute('companyid') + '"]/div/div/div[2]/a')
        lang_num = ranNo(0, lang.__len__() - 2)
        lang[lang_num].click()

        # 点击下一步
        driver.implicitly_wait(10)
        driver.find_element_by_id('next').click()

        driver.implicitly_wait(10)
        # 3.下首购单
        # 优先选择单品
        product_sale_sql = '''
            SELECT *
            FROM (
               SELECT pps.*
               FROM pm_product_sale pps, pm_product pp
               WHERE pps.PRODUCT_ID = pp.ID
               AND pps.order_type = '%s'
               AND pps.company_code = '%s'
               AND pps.price > 0
               AND pps.price < 500
               AND pps.del_flag = '20'
               AND pp.PRODUCT_TYPE = '10'
               ORDER BY pps.sort_num )
            WHERE ROWNUM <= 10
            '''
        product_sale = Oradao().sqlDiy(product_sale_sql % (10, conf.state))
        if product_sale['ID'].__len__() > 0:
            ran_item = ranNo(0, product_sale['ID'].__len__() - 1)
            product_sale_id = product_sale['ID'][ran_item]
        else:
            raise Exception(u'数据库中无符合要求的单品')
        productitem = driver.find_element_by_css_selector('input[productsaleid="' + str(product_sale_id) + '"]')
        productitem.send_keys('1')

        # 点击任意地方获取当前BV
        driver.find_element_by_id('grade_distributor').click()
        time.sleep(1)
        total_bv = int(driver.find_element_by_id('showOrderUl').find_element_by_class_name('amount').text)
        # 判断总BV是否满足50，否则重新设置数量
        if total_bv >= 50:
            driver.find_element_by_id('next').click()
        else:
            productitem.clear()
            time.sleep(1)
            productitem.send_keys(50 // total_bv + 1)
            driver.find_element_by_id('grade_distributor').click()
            driver.find_element_by_id('next').click()

        # 4.设置自动重消单
        product_sale = Oradao().sqlDiy(product_sale_sql % (30, conf.state))
        if product_sale['ID'].__len__() > 0:
            ran_item = ranNo(0, product_sale['ID'].__len__() - 1)
            product_sale_id = product_sale['ID'][ran_item]
        else:
            raise Exception(u'数据库中无符合要求的单品')
        time.sleep(2)
        productitem = driver.find_element_by_css_selector('input[productsaleid="' + str(product_sale_id) + '"]')
        productitem.send_keys(ranNo(0, 3))
        driver.find_element_by_id('next').click()

        # 5.填写个人信息
        driver.implicitly_wait(10)
        # 性别
        sex_el = driver.find_elements_by_name('sex')[ranNo(0, driver.find_elements_by_name('sex').__len__() - 1)]
        web_sex = sex_el.get_attribute('value')
        sex_el.click()
        # 姓名
        web_name = ranEN(5)
        driver.find_element_by_id('name').send_keys(web_name)
        # 生日
        web_birthday = '19' + str(ranNo(10, 99)) + '-0' + str(ranNo(1, 9)) + '-' + str(ranNo(10, 28))
        driver.find_element_by_id('birthDay').send_keys(web_birthday)
        # 选择国籍
        web_nation = random_select_by_id(driver, 'nationalityId', 1).get_attribute('value')
        # 选择语言
        web_lang = random_select_by_id(driver, 'languageCode', 1)
        # 选择注册类型
        web_regist = random_select_by_id(driver, 'registrationType', 1)
        if web_regist.text == u'公司' or web_regist.text == u'company':
            driver.find_element_by_id('company').send_keys(ranEN(5))
        # 日间电话
        web_day_phone = str(ranNo(10000000000, 13999999999))
        driver.find_element_by_id('daytimePhone').send_keys(web_day_phone)
        # 晚间电话
        web_night_phone = str(ranNo(10000000000, 13999999999))
        driver.find_element_by_id('eveningPhone').send_keys(web_night_phone)
        # 电话
        web_phone = str(ranNo(10000000000, 13999999999))
        driver.find_element_by_id('mobilePhone').send_keys(web_phone)
        # 邮箱
        web_mail = ranEN(6) + '@' + ranEN(2) + '.com'
        driver.find_element_by_id('email').send_keys(web_mail)
        # 国家
        web_country = random_select_by_id(driver, 'homeAddress.countryId', 1)
        # 省份
        time.sleep(2)
        # 有可能选到没有省份的国家，故选择两次
        try:
            web_province = random_select_by_id(driver, 'homeAddress.provinceId', 1)
        except:
            web_province = random_select_by_id(driver, 'homeAddress.provinceId', 1)
        # 城市
        web_city = ranEN(4)
        driver.find_element_by_id('homeAddress.cityName').send_keys(web_city)
        # 邮编
        web_postcode = str(ranNo(100000, 999999))
        driver.find_element_by_id('homeAddress.postalCode').send_keys(web_postcode)
        # 家庭住址
        web_adress = web_province.text + '-' + web_city + '-' + ranEN(4)
        driver.find_element_by_id('homeAddress.address').send_keys(web_adress)

        # 安置人编号，先判断是否自动安置
        Placement = Oradao.sqlDiy(Oradao(), 'select * from MM_MEMBER_CHANGE c where c.member_id=' + str(member['ID']) + 'and c.operate_type=50 order by c.create_date desc')
        len = Placement['ID'].__len__()
        if len == 0:
            value = 0
        else:
            value = Placement['NEW_VALUE'][0]
        if value == 0:
            driver.find_element_by_id('placementNo').send_keys(member['MEMBER_NO'])

        # SSN社会保险号/税号
        web_sin = random_select_by_id(driver, 'sinTaxType', 0)
        web_sin_no = ranNo(100000000, 999999999)
        driver.find_element_by_id('sinTaxId').send_keys(web_sin_no)
        # 账号
        web_account = web_name + '-account-' + ranEN(4)
        driver.find_element_by_id('eAccountNumber').send_keys(web_account)
        # 银行账号
        web_bank_name = 'bank-' + ranEN(4)
        driver.find_element_by_id('bankName').send_keys(web_bank_name)

        # 业务中心
        # 网页名字
        web_website_name = 'web_' + ranEN(2) + '_' + str(ranNo(10, 99))
        driver.find_element_by_id('websiteName').send_keys(web_website_name)
        # 密码及确认密码
        driver.find_element_by_id('password').send_keys('123456')
        driver.find_element_by_id('replatePassword').send_keys('123456')

        # 发货信息
        # 选择家庭住址
        driver.find_element_by_id('shipOrderAddressType0').click()

        # 自动单信息
        # 首次付款日期,选择当天日期
        driver.find_element_by_id('firstBillDate').click()
        time.sleep(1)
        driver.switch_to_frame(driver.find_element_by_tag_name('iframe'))
        # 选择第一个可选日期
        driver.find_element_by_class_name('Wwday').click()
        # driver.find_element_by_id('dpTodayInput').click()
        # driver.find_element_by_id('dpOkInput').click()
        driver.switch_to_default_content()
        driver.implicitly_wait(10)

        # 账单/付款
        # 支付方式，选择到公司支付
        driver.find_element_by_id('registerFeePayType1').click()
        # 选择账单地址
        driver.find_element_by_id('payAddressType0').click()

        # 接受条款
        driver.find_element_by_id('isAcceptTerms').click()
        # 提交申请
        driver.find_element_by_id('next').click()
        driver.implicitly_wait(10)

        # 验证注册信息
        rs = driver.find_elements_by_xpath('//div[@class="panel-body"]/div/div/ul/li')
        if rs.__len__() > 0:
            # 验证会员编号
            # 会员姓名验证
            self.assertEqual(rs[0].text, web_name)
        else:
            error_msg = ''
            error = driver.find_elements_by_class_name('formErrorContent')
            for i in range(error.__len__()):
                error_msg += error[i].text
            raise Exception(u'提交注册信息失败,提示为' + error_msg)
        # 会员ID
        rs_member_no = rs[1].find_element_by_tag_name('span').text
        # 推荐人名称
        rs_sponsor_name = rs[3].find_element_by_tag_name('span').text

        member_sql = 'select * from mm_member where member_no = \'%s\''
        sponsor_sql = 'select * from mm_member where id = \'%s\''
        member_db = Oradao().sqlDiy(member_sql % rs_member_no)
        if member_db['ID'].__len__() == 1:
            # 验证推荐人,安置人
            rs_sponsor_id = member_db['SPONSOR_ID'][0]
            rs_placement_id = member_db['PLACEMENT_ID'][0]
            sponsor_db = Oradao().sqlDiy(sponsor_sql % rs_sponsor_id)
            placement_db = Oradao().sqlDiy(member_sql % member['MEMBER_NO'])
            # 验证推荐人,安置人ID是否一致
            self.assertEquals(rs_sponsor_name, sponsor_db['NAME'][0])
            self.assertEquals(rs_placement_id, placement_db['ID'][0])

            # 验证性别
            self.assertEquals(member_db['GENDER'][0], web_sex)
            # 验证国籍
            self.assertEquals(str(member_db['NATIONALITY_ID'][0]), web_nation)
            # 验证生日
            self.assertEquals(member_db['BIRTHDAY'][0].strftime('%Y-%m-%d'), web_birthday)
            # 验证日间电话
            self.assertEquals(member_db['TELEPHONE'][0], web_day_phone)
            # 验证晚间电话
            self.assertEquals(member_db['EVENING_PHONE'][0], web_night_phone)
            # 验证电话
            self.assertEquals(member_db['MOBILE_PHONE'][0], web_phone)
            # 验证邮箱
            self.assertEquals(member_db['EMAIL'][0], web_mail)
        else:
            raise Exception(u'会员信息验证失败')

        # 验证登录成功
        driver.find_element_by_class_name('ots').find_element_by_tag_name('a').click()
        driver.implicitly_wait(10)
        driver.find_element_by_id('password').send_keys('123456')
        driver.find_element_by_id('btnLogin').click()

        driver.implicitly_wait(10)
        # 将顶部会员信息分割开，取编码
        bo_member_no = driver.find_element_by_class_name('username-hide-mobile').text.split('|')[1].strip(' ')
        # 验证会员编码
        self.assertEquals(rs_member_no, bo_member_no)


if __name__ == '__main__':
    unittest.main()