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
from ..pad import pad  # 用于兼容字符串传参不能删


class AES:
    """
    AES加密解密类。

    提供AES加密和解密的功能，支持ECB和CBC模式，以及自定义填充方式。
    """

    @staticmethod
    def encrypt(data: str, key: bytes, options: Options|dict|str, padding="Pkcs7", iv=None) -> AESEncryptData:
        """
        对给定数据进行AES加密。

        参数:
        data: 需要加密的字符串数据。
        key: 加密使用的密钥，必须是bytes类型。
        options: 加密选项，可以是Options对象、字典或字符串。字符串形式时，通过eval解析模式和填充方式。
        padding: 填充方式，默认为"Pkcs7"。仅在options为字符串时有效。
        iv: 初始化向量，默认为None。仅在CBC模式下需要。

        返回:
        AESEncryptData对象，包含加密后的数据。
        """
        # 解析UTF-8编码的data
        data = Utf8.parse(data)
        # 将options字典转换为Options对象
        if isinstance(options, dict):
            options = Options(**options)
        # 将options字符串转换为Options对象
        if isinstance(options, str):
            options = Options(mode=eval(f"mode.{options}"), padding=eval(f"pad.{padding}"), iv=iv)
        # 根据选项的模式进行加密操作
        match options.mode:
            case mode.ECB:
                cipher = aes.new(key=key, mode=options.mode)
                padded_data = options.padding.pad(data)
                encrypted_data = cipher.encrypt(padded_data)
                return AESEncryptData(encrypted_data)
            case mode.CBC:
                cipher = aes.new(key=key, mode=options.mode, iv=options.iv)
                padded_data = options.padding.pad(data)
                encrypted_data = cipher.encrypt(padded_data)
                return AESEncryptData(encrypted_data)

    @staticmethod
    def decrypt(data: str, key: bytes, options: Options|dict|str, padding="Pkcs7", iv=None) -> AESDecryptData:
        """
        对AES加密后的数据进行解密。

        参数:
        data: 需要解密的加密数据字符串。
        key: 解密使用的密钥，必须是bytes类型。
        options: 解密选项，可以是Options对象、字典或字符串。字符串形式时，通过eval解析模式和填充方式。
        padding: 填充方式，默认为"Pkcs7"。仅在options为字符串时有效。
        iv: 初始化向量，默认为None。仅在CBC模式下需要。

        返回:
        AESDecryptData对象，包含解密后的数据。
        """
        # 将options字典转换为Options对象
        if isinstance(options, dict):
            options = Options(**options)
        # 将options字符串转换为Options对象
        if isinstance(options, str):
            options = Options(mode=eval(f"mode.{options}"), padding=eval(f"pad.{padding}"), iv=iv)
        # 根据选项的模式进行解密操作
        match options.mode:
            case aes.MODE_ECB:
                cipher = aes.new(key, options.mode)
                return AESDecryptData(cipher, data, options.padding)
            case aes.MODE_CBC:
                cipher = aes.new(key, options.mode, iv=options.iv)
                return AESDecryptData(cipher, data, options.padding)

