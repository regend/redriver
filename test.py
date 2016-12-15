import os
from selenium import webdriver

os.environ["webdriver.chrome.driver"] = "C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"

driver = webdriver.PhantomJS()
driver.get("http://www.baidu.com")
print driver.page_source

