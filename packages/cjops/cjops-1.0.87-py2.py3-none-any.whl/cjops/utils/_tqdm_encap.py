#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File : _tqdm_encap.py
@Create  : 2024-05-10 12:33
@Desc   : 封装 tqdm 进度条的通用函数
"""

from tqdm import tqdm

def process_with_progress(iterable, process_func, desc="处理中...") -> list:
    """
    使用 tqdm 封装的通用函数，用于在处理过程中显示进度条。
    对iterable每一项进行process_func处理，并返回处理后的结果列表。
    Parameters:
        iterable (iterable): 要处理的可迭代对象。
        process_func (callable): 处理每个元素的函数。
        desc (str, optional): 进度条的描述信息，默认为 "处理中..."。

    Returns:
        list: 处理后的结果列表。

    # 使用参考
    def square(x):
        import time
        time.sleep(0.1)
        return x * x

    # 使用 process_with_progress 函数处理一个列表，对每个元素求平方，并显示进度条
    input_list = [ n for n in range(1, 100) ]
    processed_results = process_with_progress(input_list, square)
    print(processed_results)
    """
    results = []
    with tqdm(iterable, desc=desc, unit="item") as pbar:
        for item in pbar:
            result = process_func(item)
            results.append(result)
    return results
