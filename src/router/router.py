# coding=utf-8
import json
import unittest
import urllib
from util.initialize import Initialize

__author__ = 'Maggie'


# router测试
class Router(unittest.TestCase):
    def testRouter(self):
        self.conf = Initialize()
        conf = self.conf
        # 参数
        # parmas = urllib.urlencode({'url': '/router/rest?appKey=00001&v=1.0&method=user.logon&format=json',
        #                            'params': '{"username": "' + conf.username + '", "password": "' + conf.password + '"}'})

        # 打开一个url的方法，返回一个文件对象
        # f = urllib.urlopen(conf.baseurl + "/router/post.jsp", parmas)
        f = urllib.urlopen(conf.baseurl + "/router/")

        # 取url返回的响应内容
        try:
            response = f.read()
            # response_to_json = json.loads(response)
            # error_flag = response_to_json['errorFlag']
        except:
            raise Exception('response : ' + response)

        # 断言
        self.assertTrue(response.__len__() > 0)


if __name__ == '__main__':
    unittest.main()
