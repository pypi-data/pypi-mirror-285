#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File : _base64_info.py
@Create  : 2024-05-10 12:25
@Desc   : base64编码解码
"""
import base64

def base64_encode(input_string: str):
    """
    对输入字符串进行base64编码

    :param input_string: 输入字符串
    """
    # 将字符串编码为字节
    input_bytes = input_string.encode('utf-8')
    # 对字节进行 Base64 编码
    encoded_bytes = base64.b64encode(input_bytes)
    # 将编码后的字节转换为字符串并返回
    return encoded_bytes.decode('utf-8')

def base64_decode(encoded_string: str):
    """
    对输入字符串进行base64解码

    :param encoded_string: 输入字符串
    """
    # 将字符串转换为字节
    encoded_bytes = encoded_string.encode('utf-8')
    # 对字节进行 Base64 解码
    decoded_bytes = base64.b64decode(encoded_bytes)
    # 将解码后的字节转换为字符串并返回
    return decoded_bytes.decode('utf-8')
