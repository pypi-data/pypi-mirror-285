from paramiko.client import SSHClient, AutoAddPolicy
from paramiko.rsakey import RSAKey
from io import StringIO
from uuid import uuid4
import time
import re

class SSH:
    def __init__(self, hostname, port=22, username='root', pkey=None, password=None, default_env=None,
                 connect_timeout=10, term=None):
        self.stdout = None
        self.client = None
        self.channel = None
        self.sftp = None
        self.exec_file = None
        self.term = term or {}
        self.eof = 'Spug EOF 2108111926'
        self.default_env = default_env
        self.regex = re.compile(r'Spug EOF 2108111926 (-?\d+)[\r\n]?')
        self.arguments = {
            'hostname': hostname,
            'port': port,
            'username': username,
            'password': password,
            'pkey': RSAKey.from_private_key(StringIO(pkey)) if isinstance(pkey, str) else pkey,
            'timeout': connect_timeout,
            'allow_agent': False,
            'look_for_keys': False,
            'banner_timeout': 30
        }

    @staticmethod
    def generate_key():
        """
        用于生成SSH密钥对
        """
        key_obj = StringIO()
        key = RSAKey.generate(2048)
        key.write_private_key(key_obj)
        return key_obj.getvalue(), 'ssh-rsa ' + key.get_base64()

    def get_client(self):
        """
        获取或创建SSH客户端（SSHClient实例）的方法。如果客户端已存在，返回现有的客户端，否则创建一个新的客户端。
        """
        if self.client is not None:
            return self.client
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy)
        self.client.connect(**self.arguments)
        return self.client

    def ping(self):
        """
        一个简单的方法，返回True，表示SSH连接正常。
        """
        return True

    def add_public_key(self, public_key):
        """
        将公钥添加到服务器上的authorized_keys文件的方法
        """
        command = f'mkdir -p -m 700 ~/.ssh && \
        echo {public_key!r} >> ~/.ssh/authorized_keys && \
        chmod 600 ~/.ssh/authorized_keys'
        exit_code, out = self.exec_command_raw(command)
        if exit_code != 0:
            raise Exception(f'add public key error: {out}')

    def exec_command_raw(self, command, environment=None):
        """
        执行原始SSH命令的方法，返回命令的退出码和输出
        """
        channel = self.client.get_transport().open_session()
        if environment:
            channel.update_environment(environment)
        channel.set_combine_stderr(True)
        channel.exec_command(command)
        code, output = channel.recv_exit_status(), channel.recv(-1)
        return code, self._decode(output)

    def exec_command(self, command, environment=None):
        """
        执行SSH命令的方法，与上述方法不同，它还解析命令输出并返回
        """
        channel = self._get_channel()
        command = self._handle_command(command, environment)
        channel.sendall(command)
        out, exit_code = '', -1
        for line in self.stdout:
            match = self.regex.search(line)
            if match:
                exit_code = int(match.group(1))
                line = line[:match.start()]
                out += line
                break
            out += line
        return exit_code, out

    def _win_exec_command_with_stream(self, command, environment=None):
        channel = self.client.get_transport().open_session()
        if environment:
            channel.update_environment(environment)
        channel.set_combine_stderr(True)
        channel.get_pty(width=102)
        channel.exec_command(command)
        stdout = channel.makefile("rb", -1)
        out = stdout.readline()
        while out:
            yield channel.exit_status, self._decode(out)
            out = stdout.readline()
        yield channel.recv_exit_status(), self._decode(out)

    def exec_command_with_stream(self, command, environment=None):
        """
        执行带有输出流的SSH命令的方法
        """
        channel = self._get_channel()
        command = self._handle_command(command, environment)
        channel.sendall(command)
        exit_code, line = -1, ''
        while True:
            line = self._decode(channel.recv(8196))
            if not line:
                break
            match = self.regex.search(line)
            if match:
                exit_code = int(match.group(1))
                line = line[:match.start()]
                break
            yield exit_code, line
        yield exit_code, line

    def put_file(self, local_path, remote_path, callback=None):
        """
        将本地文件上传到远程服务器的方法
        """
        sftp = self._get_sftp()
        sftp.put(local_path, remote_path, callback=callback, confirm=False)

    def put_file_by_fl(self, fl, remote_path, callback=None):
        sftp = self._get_sftp()
        sftp.putfo(fl, remote_path, callback=callback, confirm=False)

    def list_dir_attr(self, path):
        """
        获取远程目录的文件属性列表的方法
        """
        sftp = self._get_sftp()
        return sftp.listdir_attr(path)

    def sftp_stat(self, path):
        """
        获取远程文件的属性的方法
        """
        sftp = self._get_sftp()
        return sftp.stat(path)

    def remove_file(self, path):
        sftp = self._get_sftp()
        sftp.remove(path)

    def _get_channel(self):
        if self.channel:
            return self.channel

        counter = 0
        self.channel = self.client.invoke_shell(**self.term)
        command = '[ -n "$BASH_VERSION" ] && set +o history\n'
        command += '[ -n "$ZSH_VERSION" ] && set +o zle && set -o no_nomatch\n'
        command += 'export PS1= && stty -echo\n'
        command = self._handle_command(command, self.default_env)
        self.channel.sendall(command)
        out = ''
        while True:
            if self.channel.recv_ready():
                out += self._decode(self.channel.recv(8196))
                if self.regex.search(out):
                    self.stdout = self.channel.makefile('r')
                    break
            elif counter >= 100:
                self.client.close()
                raise Exception('Wait spug response timeout')
            else:
                counter += 1
                time.sleep(0.1)
        return self.channel

    def _get_sftp(self):
        if self.sftp:
            return self.sftp

        self.sftp = self.client.open_sftp()
        return self.sftp

    def _make_env_command(self, environment):
        if not environment:
            return None
        str_envs = []
        for k, v in environment.items():
            k = k.replace('-', '_')
            if isinstance(v, str):
                v = v.replace("'", "'\"'\"'")
            str_envs.append(f"{k}='{v}'")
        str_envs = ' '.join(str_envs)
        return f'export {str_envs}'

    def _handle_command(self, command, environment):
        new_command = commands = ''
        if not self.exec_file:
            self.exec_file = f'/tmp/spug.{uuid4().hex}'
            commands += f'trap \'rm -f {self.exec_file}\' EXIT\n'

        env_command = self._make_env_command(environment)
        if env_command:
            new_command += f'{env_command}\n'
        new_command += command
        new_command += f'\necho {self.eof} $?\n'
        self.put_file_by_fl(StringIO(new_command), self.exec_file)
        commands += f'. {self.exec_file}\n'
        return commands

    def _decode(self, content):
        """
        将字节内容解码为字符串的方法
        """
        try:
            content = content.decode()
        except UnicodeDecodeError:
            content = content.decode(encoding='GBK', errors='ignore')
        return content

    def __enter__(self):
        """
        实现了上下文管理器的__enter__方法，用于在with语句中获取SSH客户端实例
        """
        self.get_client()
        transport = self.client.get_transport()
        if 'windows' in transport.remote_version.lower():
            self.exec_command = self.exec_command_raw
            self.exec_command_with_stream = self._win_exec_command_with_stream
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        实现了上下文管理器的__exit__方法，用于在离开with语句块时关闭SSH客户端
        """
        self.client.close()
        self.client = None


if __name__ == '__main__':
    ssh = SSH('xxxxxx', 22, 'root', password='xxxxxx')
    # with ssh:
    #     command = "while true;do echo hell world;sleep 0.1;done"
    #     for code, out in ssh.exec_command_with_stream(command):
    #         print(code, out)
    
    # with ssh:
    #     ssh.put_file("scratch.py", "/tmp/scratch.py")

    # 字符串写到指定文件中,会覆盖原有文件
    with ssh:
        ssh.put_file_by_fl(StringIO("你好呀"), "/tmp/scratch.py")