# -*- coding: utf-8 -*-
# -------------------------------

# @IDE：PyCharm
# @Python：3.1x
# @Project：DP

# -------------------------------

# @fileName：_mode.py
# @createTime：2024/7/3 9:46
# @author：Primice

# -------------------------------
from typing import Literal

ECB = 1
CBC = 2
CFB = 3
OFB = 5
CTR = 6
OPENPGP = 7
CCM = 8
EAX = 9
SIV = 10
GCM = 11
OCB = 12

def getmode(name):
    return int(eval(name))

