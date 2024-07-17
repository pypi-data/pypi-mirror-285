import sys, shlex
import subprocess
from datetime import datetime, timedelta
from loguru import logger
from typing import Tuple

def exec_command(command: str, timeout=60) -> Tuple[bool, str]:
    """
    执行shell命令

    Args:
        command (str): shell命令
        timeout (int, optional): 超时时间. Defaults to 60.

    Returns:
        tuple: (返回码, 输出)
    """
    data = ''
    # 将$替换成$$
    if not command:
        raise Exception('命令不能为空')
    try:
        sub = subprocess.run(
            command,
            check=True,
            shell=True,
            timeout=timeout,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            executable='/bin/bash'  # 指定使用Bash
        )
    except Exception as e:
        logger.error(f'执行{command}报错了,请查看{e}')
        stats = False
    else:
        stats = True
        data = sub.stdout.decode('utf-8')
    return stats, data


def exec_command_realtime_output(cmd, cwd=None, timeout=None, shell=False) -> list:
    """
    执行shell命令，封装了subprocess的Popen方法，实时输出结果，支持超时停止
    :param cmd: 执行命令
    :param cwd: 更改路径
    :param timeout: 超时时间
    :param shell: 是否通过shell执行
    :return: 执行结果 list
    :raises: Exception 执行超时
    :raises: Exception 执行失败
    """
    if shell:
        cmd_list = cmd
    else:
        cmd_list = shlex.split(cmd)
    end_time = 0
    if timeout:
        end_time = datetime.now() + timedelta(seconds=timeout)
    sub = subprocess.Popen(cmd_list, cwd=cwd,
                           stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           shell=shell, bufsize=1)
    # 执行输出
    res = []
    while sub.poll() is None:
        output = sub.stdout.readline().decode('utf-8')
        if output:
            print(output.strip())
            res.append(output.strip())
        if timeout:
            if end_time <= datetime.now():
                print(Exception(f'执行超时:{cmd}'))
                raise sys.exit(1)
    # 执行结果
    if sub.returncode == 0:
        return res
    else:
        print(Exception(f'执行失败:{cmd}'))
        raise sys.exit(1)
