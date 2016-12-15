# coding=utf-8
import HTMLParser
import re
from db.ora.oradao import Oradao

__author__ = 'Regend'


# 将参数值转换成实际值
def transData(code):
    rs = {}
    # 奖衔
    if code == 'awardsInf.awards':
        rs = {'0': '无奖衔', '01': '明日之星', '02': '明星', '03': '一星钻石', '04': '二星钻石', '05': '二星钻石精英', '06': '三星钻石', '07': '四星钻石',
              '08': '五星钻石', '09': '皇冠钻石', '10': '皇冠钻石大使'}
    else:
        sql = '''
        SELECT slv.VALUE_CODE as code,
          scv.CHARACTER_VALUE as value
        FROM sys_character_value scv, sys_list_value slv, sys_list_key slk,
        sys_Character_key sck
        WHERE scv.Character_code = 'zh_CN'
        AND scv.KEY_ID IN (
        SELECT id
        FROM sys_Character_key
        WHERE Character_key IN (
        SELECT value_title
        FROM sys_list_value
        WHERE key_id = (
        SELECT id
        FROM sys_list_key
        WHERE list_code = '%s')))
        AND slk.ID = slv.KEY_ID
        AND slv.VALUE_TITLE = sck.CHARACTER_KEY
        AND sck.id = scv.KEY_ID
        '''
        data = Oradao().sqlDiy(sql % code)
        for i in range(0, data['CODE'].__len__()):
            rs[data['CODE'][i]] = data['VALUE'][i]
    return rs


def getNum(code):
    return re.findall(r"\d+\.?\d*", code.replace(',', ''))[0]


# 根据地区名获取地区id
def getAreaIdByCode(state):
    sql = 'select * from sys_area where code = \'' + state + '\''
    rs = Oradao.sqlDiy(Oradao(), sql)
    if rs['ID'].__len__() == 0:
        return None
    if 20 in rs['TYPE']:
        for i in range(rs['ID'].__len__()):
            if rs['TYPE'][i] == 20:
                return str(rs['ID'])
    else:
        return str(rs['PARENT_ID'][0])


# 获取机构ID
def get_officeid_by_code(state):
    sql = 'select * from sys_office where DEL_FLAG = 0 and code = \'' + state + '\''
    rs = Oradao.sqlDiy(Oradao(), sql)
    if rs['ID'].__len__() == 1:
        return str(rs['ID'][0])
    else:
        raise Exception(u'获取机构ID异常')


# 获取当前期别
def get_cur_week():
    sql = '''
        SELECT *
        FROM bm_weekly_batch
        WHERE status = 0
        AND date_From <= SYSDATE
        AND date_To >= SYSDATE
    '''
    data = Oradao().sqlDiy(sql)
    if data['WORKING_STAGE'].__len__() == 1:
        return data['WORKING_STAGE'][0]
    else:
        raise Exception(u'获取当前期别异常')


# 获取当前工作月
def get_cur_monthly():
    sql = '''
        SELECT *
        FROM bm_weekly_batch
        WHERE status = 0
        AND date_From <= SYSDATE
        AND date_To >= SYSDATE
    '''
    data = Oradao().sqlDiy(sql)
    if data['MONTHLY_WORKING'].__len__() == 1:
        return data['MONTHLY_WORKING'][0]
    else:
        raise Exception(u'获取当前工作月异常')


# 获取上一个期别
def get_last_stage(cur_stage):
    sql = '''select * from bm_Monthly_Batch
         where stage_Index =
         (select stage_Index from bm_Monthly_Batch where working_Stage='%s')-1'''
    data = Oradao().sqlDiy(sql % cur_stage[:-2])
    if data['WORKING_STAGE'].__len__() == 1:
        return data['WORKING_STAGE'][0]
    else:
        raise Exception(u'获取上一个期别异常')


def unescape(string):
    return HTMLParser.HTMLParser().unescape(string)


if __name__ == '__main__':
    get_officeid_by_code('TW')