# coding=utf-8
import HTMLParser
import os
import types
import cx_Oracle
from util.initialize import Initialize

__author__ = 'Regend'


class Oradao():
    def connect(self):
        os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

        conf = Initialize()

        db = cx_Oracle.connect(conf.dbuser, conf.dbpassword, conf.host)
        return db

    def sqlDiy(self, sql):
        db = Oradao().connect()
        cursor = db.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        colum = {}
        rs = []
        for i in range(cursor.description.__len__()):
            for n in range(result.__len__()):
                try:
                    # 统一转换成unicode类型
                    # if type(result[n][i]) is types.StringType:
                    # rs.append(unicode(result[n][i], "gbk"))
                    # else:

                    # 字段值为空时，处理为''
                    if result[n][i] is None:
                        rs.append('')
                    elif isinstance(result[n][i], unicode):
                        rs.append(HTMLParser.HTMLParser().unescape(result[n][i]))
                    else:
                        rs.append(result[n][i])
                except Exception as e:
                    print e
            colum[cursor.description[i][0]] = rs
            rs = []
        cursor.close
        db.close
        return colum

    def sqlCount(self, sql):
        db = Oradao().connect()
        cursor = db.cursor()
        cursor.execute(sql)
        cursor.fetchall()
        count = cursor.rowcount
        cursor.close
        db.close
        return count
