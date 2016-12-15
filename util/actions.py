# coding=utf-8
from util.ranchar import ranNo

__author__ = 'Regend'


# 随机选择下拉框，并返回其文本值
def random_select_by_id(driver, elid, index):
    el = driver.find_element_by_id(elid).find_elements_by_tag_name('option')
    if el.__len__() > 0:
        ran_el = ranNo(index, el.__len__() - 1)
        el[ran_el].click()
        return el[ran_el]
    else:
        raise Exception(u'下拉框无数据')


if __name__ == '__main__':
    print 'test'