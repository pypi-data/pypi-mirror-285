#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File : _clipboard.py
@Create  : 2024-05-10 12:30
@Desc   : 将字符串数据复制到剪贴板
"""
import pyperclip

def copy_to_clipboard(data: str) -> None:
    """
    将数据复制到剪贴板。

    Parameters:
        data (str): 要复制到剪贴板的数据。

    Returns:
        None
    """
    # 判断data是否为字符串
    if not isinstance(data, str):
        raise ValueError("Data must be a string.")

    # 使用pyperclip库将数据复制到剪贴板
    pyperclip.copy(data)
