# cython: language_level=3
# #!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author: MaJian
@Time: 2024/1/17 9:28
@SoftWare: PyCharm
@Project: mortal
@File: __init__.py
"""
from .crypt_main import *


class MortalCrypt:
    @classmethod
    def aes_ecb_encrypt(cls, value, key):
        return aes_ecb_encrypt(value, key)

    @classmethod
    def aes_ecb_decrypt(cls, value, key):
        return aes_ecb_decrypt(value, key)

    @classmethod
    def aes_cbc_encrypt(cls, value, key, iv):
        return aes_cbc_encrypt(value, key, iv)

    @classmethod
    def aes_cbc_decrypt(cls, value, key, iv):
        return aes_cbc_decrypt(value, key, iv)

    @classmethod
    def base64_encrypt(cls, value):
        return base64_encrypt(value)

    @classmethod
    def base64_decrypt(cls, value):
        return base64_decrypt(value)

    @classmethod
    def des_encrypt(cls, value, key):
        return des_encrypt(value, key)

    @classmethod
    def des_decrypt(cls, value, key):
        return des_decrypt(value, key)

    @classmethod
    def md5_encrypt(cls, value):
        return md5_encrypt(value)

    @classmethod
    def php_encrypt(cls, value, key, iv, base64s=False):
        return php_encrypt(value, key, iv, base64s)

    @classmethod
    def php_decrypt(cls, value, key, iv, base64s=False):
        return php_decrypt(value, key, iv, base64s)

    @classmethod
    def rsa_keys(cls):
        return rsa_keys()

    @classmethod
    def rsa_encrypt(cls, value, pub_key=None, hexs=False):
        return rsa_encrypt(value, pub_key, hexs)

    @classmethod
    def rsa_decrypt(cls, value, pri_key, hexs=False):
        return rsa_decrypt(value, pri_key, hexs)

    @classmethod
    def sha1_encrypt(cls, value):
        return sha1_encrypt(value)

    @classmethod
    def sha256_encrypt(cls, value):
        return sha256_encrypt(value)

    @classmethod
    def sha384_encrypt(cls, value):
        return sha384_encrypt(value)

    @classmethod
    def sha512_encrypt(cls, value):
        return sha512_encrypt(value)

    @classmethod
    def token_encrypt(cls, data, key, exp_time=86400, issuer=None):
        return token_encrypt(data, key, exp_time, issuer)

    @classmethod
    def token_decrypt(cls, token, key, issuer=None):
        return token_decrypt(token, key, issuer)
