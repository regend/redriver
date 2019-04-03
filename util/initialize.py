# coding=utf-8
import logging
import os
import xml.dom.minidom
import sys
import redis
from selenium import webdriver
import time

__author__ = 'Regend'


class Initialize():
    def __init__(self):
        pass

    sysPath = os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir)) + '\\QA-Webdriver'
    path = sysPath + '\\conf\\oss.xml'
    dom = xml.dom.minidom.parse(path)
    root = dom.documentElement

    env = root.getElementsByTagName('env')[0].childNodes[0].data
    browser = root.getElementsByTagName('browser')[0].childNodes[0].data
    driverpath = root.getElementsByTagName('driverpath')[0].childNodes[0].data

    configPath = os.path.abspath(
        os.path.join(os.path.dirname("__file__"), os.path.pardir)) + '\\QA-Webdriver\\conf\\oss-' + env + '.xml'
    configDom = xml.dom.minidom.parse(configPath)
    configRoot = configDom.documentElement

    database = configRoot.getElementsByTagName('database')[0]
    host = database.getElementsByTagName('host')[0].childNodes[0].data
    dbuser = database.getElementsByTagName('username')[0].childNodes[0].data
    dbpassword = database.getElementsByTagName('password')[0].childNodes[0].data

    redis_conf = configRoot.getElementsByTagName('redis')[0]
    redis_host = redis_conf.getElementsByTagName('host')[0].childNodes[0].data
    redis_port = redis_conf.getElementsByTagName('port')[0].childNodes[0].data
    redis_db = redis_conf.getElementsByTagName('db')[0].childNodes[0].data

    login = configRoot.getElementsByTagName('login')[0]
    username = login.getElementsByTagName('username')[0].childNodes[0].data
    password = login.getElementsByTagName('password')[0].childNodes[0].data

    baseurl = configRoot.getElementsByTagName('baseurl')[0].childNodes[0].data

    state = configRoot.getElementsByTagName('state')[0].childNodes[0].data

    datapath = configRoot.getElementsByTagName('datapath')[0].childNodes[0].data

    # 初始化redis
    r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

    # 初始化浏览器及登录
    def start(self):
        reload(sys)
        sys.setdefaultencoding('utf-8')

        self.mk_dir(self.get_build_number())
        self.log_config()

        if self.browser == 'chrome':
            os.environ["webdriver.chrome.driver"] = str(self.driverpath)
            driver = webdriver.Chrome(str(self.driverpath))
        else:
            driver = webdriver.Firefox()

        driver.maximize_window()
        driver.get(self.baseurl + '/portal/index')

        driver.find_element_by_id('username').send_keys(self.username)
        driver.find_element_by_id('password').send_keys(self.password)
        driver.find_element_by_id('btnLogin').click()
        driver.implicitly_wait(10)

        return driver

    # 切换地区
    @staticmethod
    def stateChange(driver, state=str(state)):
        driver = driver.find_element_by_id('selCompanyCode')
        driver.find_element_by_xpath('//option[@value="' + state + '"]').click()

    # 切换语言
    @staticmethod
    def langChange(driver, lang):
        driver = driver.find_element_by_id('selLocale')
        driver.find_element_by_xpath('//option[@value="' + lang + '"]').click()

    # 获取地区的显示名称，只能在切换到iframe之前进行
    def getState(self, driver):
        driver = driver.find_element_by_id('selCompanyCode')
        return driver.find_element_by_xpath('//option[@value="' + str(self.state) + '"]').text

    # 截屏
    def getScreenshot(self, obj, file_name=''):
        build_number = self.get_build_number()
        path = self.datapath + build_number + '\\screenshot\\'
        obj.driver.get_screenshot_as_file(path + obj._testMethodName.lstrip('test') + file_name + '.jpg')
        obj.driver.execute_script('scrollTo(0,10000)')
        time.sleep(1)
        obj.driver.get_screenshot_as_file(path + obj._testMethodName.lstrip('test') + '-bottom' + file_name + '.jpg')

    # 将build_number存入redis
    def set_build_number(self, build_number=0, mkdir=True):
        self.r.set('build_number', build_number)
        if mkdir:
            self.mk_dir(build_number)

    # 从redis取出将build_number存入redis
    def get_build_number(self):
        build_number = self.r.get('build_number')
        if build_number is None:
            return 0
        else:
            return build_number

    # 创建文件夹
    def mk_dir(self, build_number=0):
        path = self.datapath + build_number
        if not os.path.exists(path + '\\screenshot'):
            try:
                os.makedirs(path + '\\screenshot')
            except:
                raise Exception(u'创建截屏文件夹异常')
        if not os.path.exists(path + '\\log'):
            try:
                os.makedirs(path + '\\log')
            except:
                raise Exception(u'创建日志文件夹异常')

    def log_config(self):
        # 初始化log配置
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(funcName)s-%(levelname)s:%(message)s',
                            datefmt='%d %b %Y %H:%M:%S',
                            filename=self.datapath + self.r.get('build_number') + '\\log\\webdriver.log',
                            filemode='a')


if __name__ == "__main__":
    Initialize().set_build_number('123')
