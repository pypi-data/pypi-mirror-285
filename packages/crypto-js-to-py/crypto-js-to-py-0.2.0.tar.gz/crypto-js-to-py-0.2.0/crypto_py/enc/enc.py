# -*- coding: utf-8 -*-
# -------------------------------

# @IDE：PyCharm
# @Python：3.1x
# @Project：DP

# -------------------------------

# @fileName：_enc.py
# @createTime：2024/7/3 9:49
# @author：Primice

# -------------------------------

class Utf8:
    @staticmethod
    def parse(_data: str):
        return _data.encode('utf-8')


class Hex:
    @staticmethod
    def parse(_data: str):
        return _data.encode("utf-8").hex()
