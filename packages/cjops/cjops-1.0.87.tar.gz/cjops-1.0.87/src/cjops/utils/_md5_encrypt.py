#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File : _md5_encrypt.py
@Create  : 2024-05-10 12:31
@Desc   : md5加密
"""

import hashlib
from typing import Any

def md5_encrypt(input_string: str, salt: Any = None):
    """
    对输入字符串进行md5加密

    :param input_string: 输入字符串
    :param salt: 盐值，可以不填
    """
    use_salt_bool = False

    if salt is not None:
        try:
            salt = str(salt)
        except Exception as e:
            raise Exception(f"salt转化为字符串失败, {e}")
        use_salt_bool = True

    md5 = hashlib.md5()
    if use_salt_bool:
        salt = salt.encode('utf-8')
        md5.update(input_string.encode('utf-8') + salt)
    else:
        md5.update(input_string.encode('utf-8'))
    return md5.hexdigest()
