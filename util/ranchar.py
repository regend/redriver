# coding=utf-8
import random

__author__ = 'Regend'


# 随机英文
def ranEN(num):
    seed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    sa = []
    for i in range(num):
        sa.append(random.choice(seed))
    salt = ''.join(sa)
    return salt


# 随机整数,包括a,b
def ranNo(a, b):
    if a == b:
        return b
    else:
        return random.randint(a, b)


# 随机小数，a:左边界，b:右边界，c:小数点精确度
def ranFloat(a, b, c):
    if a == b:
        return b
    else:
        if c == 1:
            rs = random.uniform(a, b)
            return "%.1f" % float(rs)
        elif c == 2:
            rs = random.uniform(a, b)
            return "%.2f" % float(rs)
        elif c == 3:
            rs = random.uniform(a, b)
            return "%.3f" % float(rs)
        elif c == 4:
            rs = random.uniform(a, b)
            return "%.4f" % float(rs)
        elif c == 5:
            rs = random.uniform(a, b)
            return "%.5f" % float(rs)
        else:
            rs = random.uniform(a, b)
            return "%.1f" % float(rs)


def ranZN():
    head = random.randint(0xB0, 0xDF)
    body = random.randint(0xA, 0xF)
    tail = random.randint(0, 0xF)
    val = (head << 0x8) | (body << 0x4) | tail
    str = "%x" % val
    return str.decode('hex').decode('GBK', 'ignore')


# 随机中文
def ranZNS(times=1):
    char = ""
    for n in range(0, times):
        charbase = ranZN()
        char += charbase
    return char


if __name__ == '__main__':
    print ranNo(0, 0)