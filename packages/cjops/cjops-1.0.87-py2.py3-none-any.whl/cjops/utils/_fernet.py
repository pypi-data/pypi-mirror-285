#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File : _fernet.py
@Create  : 2024-05-10 12:31
@Desc   : 使用Fernet库进行加密和解密
"""
from cryptography.fernet import Fernet

def fernet_generate_key():
    """
    生成一个随机的Fernet密钥
    """
    return Fernet.generate_key().decode('utf-8')

def fernet_jiami(input_string: str, key: str):
    """
    使用Fernet库对输入的字符串进行加密
    :param input_string: 要加密的字符串
    :param key: Fernet密钥
    """
    # 检查Fernet密钥是否符合格式
    try:
        key = str(key).encode('utf-8')
        # 创建 Fernet 对象
        cipher_suite = Fernet(key)
    except Exception as e:
        mes = f"Fernet密钥格式错误: {e},请使用Fernet.generate_key()生成密钥"
        raise Exception(mes)

    # 将字符串转换为字节型
    input_bytes = input_string.encode('utf-8')
    # 加密字符串
    encrypted_text = cipher_suite.encrypt(input_bytes).decode('utf-8')
    return encrypted_text

def fernet_jiemi(input_string: str, key: str):
    """
    使用Fernet库对输入的字符串进行解密
    :param input_string: 要解密的字符串
    :param key: Fernet密钥
    """

    # 检查Fernet密钥是否符合格式
    try:
        key = str(key).encode('utf-8')
        # 创建 Fernet 对象
        cipher_suite = Fernet(key)
    except Exception as e:
        mes = f"Fernet密钥格式错误: {e}"
        raise Exception(mes)

    # 将字符串转换为字节型
    input_bytes = input_string.encode('utf-8')

    # 解密字符串
    decrypted_text = cipher_suite.decrypt(input_bytes).decode('utf-8')
    return decrypted_text
