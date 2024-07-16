# -*- coding: utf-8 -*-
# -------------------------------

# @IDE：PyCharm
# @Python：3.1x
# @Project：crypto-js-to-py

# -------------------------------

# @fileName：_pad.py
# @createTime：2024/7/3 9:50
# @author：Primice

# -------------------------------
from abc import ABC, abstractmethod


class Pad(ABC):
    @staticmethod
    @abstractmethod
    def pad(self):
        pass

    @staticmethod
    @abstractmethod
    def unpad(self):
        pass


class Pkcs7(Pad):
    @staticmethod
    def pad(_data, block_size: int = 16):
        padding_length = block_size - len(_data) % block_size
        if isinstance(_data, list):
            return _data + [padding_length] * padding_length
        return _data + bytes([padding_length] * padding_length)

    @staticmethod
    def unpad(_data):
        return _data[:-_data[-1]]


class NoPadding(Pad):
    @staticmethod
    def pad(_data, block_size: int = 16):
        padding_length = block_size - len(_data) % block_size

        if isinstance(_data, list):
            return _data + [0] * padding_length
        return _data + padding_length * b'\0'

    @staticmethod
    def unpad(_data):
        if isinstance(_data, list):
            return _data[:_data.index(0)]
        return _data.rstrip('\0')
