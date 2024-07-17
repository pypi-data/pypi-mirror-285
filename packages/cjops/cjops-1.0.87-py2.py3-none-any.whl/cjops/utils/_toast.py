#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File : _toast.py
@Create  : 2024-05-10 12:32
@Desc   : 带有表情的消息提示
"""
import emoji

def _validate_message_type(func):
    def wrapper(message):
        if not isinstance(message, str):
            print(message)  # 如果message不是字符串类型，则直接输出message
            return None  # 返回None，不执行被装饰的函数
        else:
            return func(message)  # 如果message是字符串类型，则执行被装饰的函数
    return wrapper

@_validate_message_type
def success_toast(message: str):
    """
    输出成功消息，并添加成功的表情符号
    """
    success_emoji = emoji.emojize(':thumbs_up:' * 3, language='alias')
    print(f"{success_emoji} Success: {message}")

@_validate_message_type
def warning_toast(message: str):
    """
    输出警告消息，并添加警告的表情符号
    """
    warning_emoji = emoji.emojize(':warning:' * 3, language='alias')
    print(f"{warning_emoji} Warning: {message}")

@_validate_message_type
def failure_toast(message: str):
    """
    输出失败消息，并添加失败的表情符号
    """
    failure_emoji = emoji.emojize(':thumbs_down:' * 3, language='alias')
    print(f"{failure_emoji} Failure: {message}")
