# -*- coding: utf-8 -*-
# -------------------------------

# @IDE：PyCharm
# @Python：3.1x
# @Project：DP

# -------------------------------

# @fileName：_aes.py
# @createTime：2024/7/3 9:51
# @author：Primice

# -------------------------------
from Cryptodome.Cipher import AES as aes

from ..models._options import Options
from ..models._data_models import AESDecryptData,AESEncryptData
from ..enc.enc import Utf8
from ..mode import mode
from ..pad import pad  # 不能删


class AES:
    @staticmethod
    def encrypt(data: str, key: bytes, options: Options|dict|str,padding="Pkcs7",iv=None) -> AESEncryptData:

        data = Utf8.parse(data)
        if isinstance(options,dict):
            options = Options(**options)
        if isinstance(options,str):
            options = Options(mode=eval(f"mode.{options}"),padding=eval(f"pad.{padding}"),iv=iv)
        match options.mode:
            case mode.ECB:
                cipher = aes.new(key=key, mode=options.mode)
                padded_data = options.padding.pad(data)
                # padded_data = data.encode('utf-8') + (16 - len(data.encode('utf-8')) % 16) * b'\0'
                encrypted_data = cipher.encrypt(padded_data)
                return AESEncryptData(encrypted_data)
            case mode.CBC:
                cipher = aes.new(key=key, mode=options.mode, iv=options.iv)
                padded_data = options.padding.pad(data)
                # padded_data = data.encode('utf-8') + (16 - len(data.encode('utf-8')) % 16) * b'\0'
                encrypted_data = cipher.encrypt(padded_data)
                return AESEncryptData(encrypted_data)

    @staticmethod
    def decrypt(data: str, key: bytes, options: Options|dict|str,padding="Pkcs7",iv=None) -> AESDecryptData:

        if isinstance(options,dict):
            options = Options(**options)
        if isinstance(options,str):
            options = Options(mode=eval(f"mode.{options}"),padding=eval(f"pad.{padding}"),iv=iv)

        match options.mode:
            case aes.MODE_ECB:
                cipher = aes.new(key, options.mode)
                return AESDecryptData(cipher, data, options.padding)
            case aes.MODE_CBC:
                cipher = aes.new(key, options.mode, iv=options.iv)
                return AESDecryptData(cipher, data, options.padding)

