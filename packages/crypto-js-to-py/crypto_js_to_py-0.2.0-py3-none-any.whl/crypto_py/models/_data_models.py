# -*- coding: utf-8 -*-
# -------------------------------

# @IDE：PyCharm
# @Python：3.1x
# @Project：crypto-js-to-py

# -------------------------------

# @fileName：_data_models.py
# @createTime：2024/7/12 17:16
# @author：Primice


from Cryptodome.Cipher import AES
from typing import Type
import base64
import binascii

from ..enc.enc import Utf8
from ..pad.pad import Pad

class AESDecryptData:
    """ AES的解密数据对象。

    实例化后的类可以通过decode()方法获取utf8解密内容
    十六进制密文也可以通过ciphertext()方法来获取hex解密内容

    example:
        cipher = AES.new(...)
        data:str = "..."
        padding = unpad(....)

        decrypter = DecryptDate(cipher,data,padding)
        print(decrypter.decode("utf-8"))
    or:
        print(decrypter.ciphertext.decode("utf-8"))

    """
    def __init__(self, cipher: AES, data: str, padding: Type[Pad]):
        """初始化函数

        @param cipher : AES实例
        @param data : 密文字符串
        @param padding : Pad子类实例 例如 Pkcs7 NoPadding

        """
        self._data = data
        self.__padding = padding
        self.__cipher = cipher

    def decode(self) -> bytes:
        data = Utf8.parse(self._data)
        decrypted_data = self.__cipher.decrypt(base64.decodebytes(data))
        return self.__padding.unpad(decrypted_data).decode()

    @property
    def ciphertext(self) -> bytes:
        decrypted_data = self.__cipher.decrypt(binascii.unhexlify(self._data))
        return self.__padding.unpad(decrypted_data)

    def __str__(self) -> str:
        return f"<class AESDecryptData data:'{self._data[:10]}'>"


class AESEncryptData:
    """AES密文的对象

    因为实例化时传进来的值已经是密文，因此decode()和ciphertext只做编码过程

    """
    def __init__(self, encrypted_data):
        self.encrypted_data = encrypted_data

    def decode(self) -> str:
        return str(base64.encodebytes(self.encrypted_data), encoding='utf-8').replace('\n', '')

    @property
    def ciphertext(self) -> bytes:
        return binascii.hexlify(self.encrypted_data)

    def __str__(self) -> str:
        return f"<class EncryptData data:'{self.encrypted_data}'>"

class SM4EncryptData:
    def __init__(self, out_array: bytes | bytearray, decode_mode='base64'):
        self.decode_mode = decode_mode
        self._out_array = out_array

    def decode(self):
        # 密文数组转换为字符串
        if self.decode_mode == 'base64':
            return base64.b64encode(self._out_array).decode()
        else:
            # 文本模式
            return bytes(self._out_array).decode()