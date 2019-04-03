# coding=utf-8

from util.initialize import Initialize

__author__ = 'Regend'


class MemberInfo:
    def __init__(self):
        self.verificationErrors = []
        self.conf = Initialize()
        self.driver = self.conf.start()

    def check(self):
        # self.conf.getScreenshot(self)

        driver = self.driver
        driver.implicitly_wait(10)

        # MM001 会员信息维护-查询
        driver.get("https://oss.jmtop.com/ossMember/mm/member/list")
        driver.implicitly_wait(10)
        try:
            driver.find_element_by_id('btnSubmit')
            print u'系统正常'
            driver.quit()
        except:
            print driver.page_source
            driver.quit()
            raise Exception(u'系统异常')


if __name__ == '__main__':
    MemberInfo().check()