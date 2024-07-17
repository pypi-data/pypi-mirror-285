import sys
from pathlib import Path
import pendulum
import csv
from typing import List, Dict, Any, Tuple, Union
from loguru import logger

def write_csv(data: Union[List, Tuple, List[Dict[str, Any]], List[Tuple], List[List[Any]]], filename: str = None, stdout: bool = False, fieldnames: Union[List[str], Tuple[str]] = None):
    """
    将数据写入CSV 文件或者打印到控制台

    Args:
        data (List): 要写入的数据，可以是字典列表、元组列表或二维列表。
        filename (str): 要写入的文件名。如果未提供文件名，则将数据写入标准输出（控制台）。
        stdout (Bool): 是否将数据写入标准输出（控制台）。如果为 True，则将数据写入标准输出，否则将数据写入文件。
    Raises:
        ValueError: 如果数据类型不正确
    """
    if not isinstance(data, (list, tuple)):
        raise ValueError("Data must be a list or tuple.")

    if not data:
        raise Exception("Data cannot be empty.")

    # 判断传递fieldnames是否正确
    if fieldnames and not isinstance(fieldnames, (tuple, list)):
        raise ValueError("fieldnames must be a list or tuple.")

    # 没有传递头部,自动获取fieldnames
    if not fieldnames:
        first_item = data[0]
        if isinstance(first_item, dict):
            # 获取所有字段名
            fieldnames = []
            for item in data:
                for k in item.keys():
                    if k not in fieldnames:
                        fieldnames.append(k)
        elif isinstance(first_item, (tuple, list)):
            # 获取data中的item,最长的item长度
            max_length = max(len(item) for item in data)
            fieldnames = [f"col_{i+1}" for i in range(max_length)]
        elif isinstance(first_item, (int, float, str)):
            fieldnames = ['col_1']
        else:
            raise ValueError("Unsupported data type.")

    # 写入CSV文件或标准输出
    if not stdout:
        # 判断文件是否已经存在,则报错退出
        if filename:
            if Path(filename).exists():
                logger.warning(f'{filename}文件已经存在,开始删除')
                # 删除此文件
                Path(filename).unlink()
        if not filename:
            filename = f'output-{pendulum.now().to_datetime_string()}.csv'
        with open(filename, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=list(fieldnames))
            writer.writeheader()
            for item in data:
                if item:
                    if isinstance(item, dict):
                        writer.writerow(item)
                    elif isinstance(item, (tuple, list)):
                        writer.writerow(dict(zip(fieldnames, item)))
                    elif isinstance(item, (int, float, str)):
                        writer.writerow({fieldnames[0]: item})
            print(f"Data written to {filename}.")
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:
            if item:
                if isinstance(item, dict):
                    writer.writerow(item)
                elif isinstance(item, (tuple, list)):
                    writer.writerow(dict(zip(fieldnames, item)))
                elif isinstance(item, (int, float, str)):
                    writer.writerow({fieldnames[0]: item})

def _remove_bom(file_path: str) -> str:
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        content = file.read()
    return content

def read_csv(file_path: str) -> list:
    # 去除 BOM, BOM是字节顺序标记（Byte Order Mark）的缩写，是一种特殊的字符序列，用于标识文本文件的编码方式和字节顺序,它通常出现在 Unicode编码的文本文件开头,用来指示文件的编码方式和字节顺序。
    content = _remove_bom(file_path)

    # 使用 StringIO 创建一个类文件对象，用于向 csv.reader 或 csv.DictReader 传递文件内容
    from io import StringIO
    file_like_object = StringIO(content)

    # 使用csv.DictReader读取文件内容，并指定字段名
    csv_reader = csv.DictReader(file_like_object)

    # 读取文件中的每一行，并将其存储为字典列表
    data = list(csv_reader)

    return data

if __name__ == '__main__':
    data_list = [
        1, 'Alice', 'Female', 25
    ]
    write_csv(data_list)
