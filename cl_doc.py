# coding=utf-8
import logging
import os
import time
import sys
from util.initialize import Initialize

__author__ = 'Regend'


def doc_list(path=Initialize().datapath):
    dir_name = os.listdir(path)
    if dir_name.__len__() == 0:
        try:
            os.rmdir(path)
            logging.info(u'删除文件夹成功-' + path)
        except:
            raise Exception(u'删除文件夹失败，请查看文件权限')
    for i in range(dir_name.__len__()):
        if os.path.isdir(path + dir_name[i]):
            if dir_name[i] == 'SLNM_Script':
                pass
            else:
                doc_list(path + dir_name[i] + '\\')
        elif os.path.isfile(path + dir_name[i]):
            clear_doc(path + dir_name[i])


def clear_doc(file_name):
    now = time.time()
    file_time = os.stat(file_name).st_mtime
    # 文件修改时间超过当前时间一个月，则删除
    if now - file_time > 2592000:
        os.remove(file_name)
        logging.info(u'删除文件成功-' + file_name)
    else:
        pass


if __name__ == "__main__":
    Initialize().set_build_number(sys.argv[1], True)
    Initialize().log_config()
    doc_list()