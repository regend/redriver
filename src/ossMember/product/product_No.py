# coding=utf-8
import unittest

from selenium.webdriver import ActionChains
from util.initialize import Initialize
from util.ranchar import ranNo, ranEN


__author__ = 'Regend'


class ProductNo(unittest.TestCase):
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

    def testProduct(self):
        # 初始化登录
        driver = self.driver
        conf = self.conf
        conf.stateChange(driver)
        driver.implicitly_wait(10)

        # 选择运营支撑平台
        driver = self.driver
        driver.find_element_by_id('topMenu_1100').click()
        button = driver.find_element_by_id('left_menu_1110')
        menu = driver.find_element_by_class_name('nav-header')

        # 鼠标悬停在商品管理上
        chain = ActionChains(driver)
        chain.move_to_element(button).perform()
        driver.find_element_by_xpath('//li[@id="left_menu_1111"]/a/span').click()
        chain.move_to_element(menu).perform()

        driver.implicitly_wait(10)
        # 切换至iframe
        driver.switch_to_frame('contentIframe1111')

        # 添加商品
        driver.find_element_by_id('btnAdd').click()

        driver.implicitly_wait(10)
        # 初始化下拉框element:0:商品类别;1:单位;2:销售类别
        # selects = driver.find_elements_by_class_name('select2-choice')
        # 商品类别下拉框,通过js加载的div下拉菜单
        # selects[0].click()
        # 获取商品类别下拉菜单选项数量，去掉第一个空值，随机选择一项
        ranProductOp = ranNo(1, driver.find_elements_by_xpath('//select[@name="productType"]/option').__len__())
        productOp = driver.find_element_by_xpath('//select[@name="productType"]/option[' + str(ranProductOp) + ']')
        productText = productOp.text
        productOp.click()

        driver.implicitly_wait(10)

        # 输入随机商品编码
        product_No = str(ranNo(100000, 999999))
        driver.find_element_by_id('productNo').send_keys(product_No)
        # 输入随机商品名称
        product_name = ranEN(8)
        driver.find_element_by_id('productName').send_keys(product_name)

        # 选择单位
        # selects[1].click()
        ranUnitOp = ranNo(1, driver.find_elements_by_xpath('//select[@name="unitNo"]/option').__len__())
        unitOp = driver.find_element_by_xpath('//select[@name="unitNo"]/option[' + str(ranUnitOp) + ']')
        unitText = unitOp.text
        unitOp.click()

        # 选择销售类别
        # selects[2].click()
        ranSaleOp = ranNo(1, driver.find_elements_by_xpath('//select[@name="smNo"]/option').__len__())
        saleOp = driver.find_element_by_xpath('//select[@name="smNo"]/option[' + str(ranSaleOp) + ']')
        saleText = saleOp.text
        saleOp.click()

        # 设置体积
        ranVolume = str(ranNo(1, 5000)) + '.00'
        driver.find_element_by_xpath('//div[@id="tabs"]/div[2]/div[1]/div/div[1]/div/div[6]/div/div/span[1]/input[1]').send_keys(ranVolume)

        # 设置重量
        ranWeight = str(ranNo(1, 5000)) + '.00'
        driver.find_element_by_xpath('//div[@id="tabs"]/div[2]/div[1]/div/div[1]/div/div[7]/div/div/span[1]/input[1]').send_keys(ranWeight)

        # 编辑备注
        remarkText = u'备注' + ranEN(6)
        driver.find_element_by_id('remark').send_keys(remarkText)

        # 保存/取消
        driver.find_element_by_id('btnSubmit').click()
        # driver.find_element_by_id('btnCancel').click()

        driver.implicitly_wait(10)

        # 搜索新增的商品编码
        driver.find_element_by_name('sp_productNo_LIKE').send_keys(product_No)
        # 保存后页面会稍微往下拉，查询按钮被挡住点击不了，需要切换到父iframe将页面往上拉
        driver.switch_to_default_content()
        driver.execute_script('scrollTo(0,0)')
        driver.switch_to_frame('contentIframe1111')
        driver.find_element_by_id('btnSubmit').click()
        rsNum = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr').__len__()
        rsXpath = driver.find_elements_by_xpath('//table[@id="contentTable"]/tbody/tr[' + str(rsNum) + ']/td')

        # 获取页面各字段数值-0:商品编码;1:编码名称;2:商品类别;3:体积;4:重量;
        rsProductNo = rsXpath[0].text
        rsProductName = rsXpath[1].text
        rsProductKind = rsXpath[2].text
        rsProductVolume = rsXpath[3].text
        rsProductWeight = rsXpath[4].text

        # 断言
        self.assertEquals(rsProductNo, product_No)
        self.assertEquals(rsProductName, product_name)
        self.assertEquals(rsProductKind, productText)
        self.assertEquals(rsProductVolume, ranVolume)
        self.assertEquals(rsProductWeight, ranWeight)

if __name__ == '__main__':
    unittest.main()