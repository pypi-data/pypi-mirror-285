import os, sys, re
from setuptools import setup, Command
from pathlib import Path

# 默认上传包cjops
package = 'cjops'
packages = ['cjops', 'cjops.utils', 'cjops.aliyun', 'cjops.template']

if Path('deploy').exists():
    with open('deploy', 'r', encoding='utf-8') as f:
        line = f.read().strip()
        if line == 'k9s':
            package = line if line else 'cjops'
            packages = ['k9s', 'k9s.search', 'k9s.get']
        if line == 'pycj':
            package = line if line else 'cjops'
            packages = ['pycj']

if 'upload' in sys.argv:
    if sys.argv[-1] in ['k8', 'k8s', 'k9', 'k9s']:
        with open('deploy', 'w', encoding='utf-8') as f:
            f.write('k9s')
            package = 'k9s'
            packages = ['k9s', 'k9s.search', 'k9s.get']
        sys.argv.pop(len(sys.argv) -1)

    if sys.argv[-1] in ['pyc', 'pycj', 'command', 'pycommand']:
        with open('deploy', 'w', encoding='utf-8') as f:
            f.write('pycj')
            package = 'pycj'
            packages = ['pycj']
        sys.argv.pop(len(sys.argv) -1)

about = {}
here = Path(__file__).absolute().parent
version_file_path = here /"src" / package / "__version__.py"
with open(version_file_path, "r", encoding="utf-8") as f:
    # exec() 函数用于执行从文件中读取的 Python 代码。具体来说，exec() 函数可以接受字符串形式的Python代码并执行,或者从文件中读取代码并执行。
    # 在你的例子中，通过打开文件 __version__.py 并读取其中的内容，然后使用 exec() 函数执行这些代码，将执行结果存储在 about 字典中。这种做法通常用于从外部文件中加载配置、定义变量或执行一些特定的操作。
    f_read_string = f.read()
    exec(f_read_string, about)

    if 'upload' in sys.argv:
        last_number_str = str(int(str(about['__version__']).split('.')[-1])+1)
        l = about['__version__'].split('.')[:-1]
        l.append(last_number_str)
        about['__version__'] = '.'.join(l)

        # 将新的__version__写入到文件中
        pattern = r'(__version__\s*=\s*")(\d+\.\d+\.\d+)(")'
        updated_content = re.sub(pattern, r'\g<1>' + about['__version__'] + r'\g<3>', f_read_string)
        with open(version_file_path, 'w') as f:
            f.write(updated_content)

with open("README.md", "r") as fh:
    long_description = fh.read()

cjops_requires = [
        'aliyun-log-python-sdk==0.8.15',
        'requests>=2.27.1',
        'loguru>=0.6.0',
        'dnspython>=2.3.0',
        'pandas>=1.1.5',
        'pendulum>=2.1.2',
        'pymysql>=1.0.2',
        'openpyxl>=3.1.2',
        'yagmail>=0.15.293',
        'tqdm>=4.66.2',
        'pyperclip>=1.8.2',
        'emoji>=2.11.1',
        'paramiko==3.4.0',
        'cryptography'
]

k9s_requires = [
        'loguru>=0.6.0',
        'cjops>=1.0.10'
]

pyc_requires = [
    'typer',
    'cryptography',
    'dnspython>=2.3.0',
    'pendulum>=2.1.2',
    'loguru>=0.6.0',
]

# 确定依赖包
require_package = cjops_requires
if package == 'k9s':
    require_package = k9s_requires
elif package == 'pycj':
    require_package = pyc_requires

class UploadCommand(Command):
    """Support setup.py upload."""
    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        package = 'cjops'
        packages = ['cjops', 'cjops.utils', 'cjops.aliyun', 'cjops.template']

        if Path('deploy').exists():
            with open('deploy', 'r', encoding='utf-8') as f:
                line = f.read().strip()
                if line == 'k9s':
                    package = line if line else 'cjops'
                    packages = ['k9s', 'k9s.search', 'k9s.get']
                if line == 'pycj':
                    package = line if line else 'cjops'
                    packages = ['pycj']

        self.status("Removing previous builds…")
        os.system("rm -rf build cjops.egg-info k9s.egg-info src/cjops.egg-info src/k9s.egg-info dist src/pycj.egg-info pycj.egg-info")

        self.status('start building wheel')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload --skip-existing dist/* -r localhost -u caojie -p AmxNg41cfiRiDsfZ')
        # 上传官网安装,默认不上传
        # pip uninstall cjops -y && pip install -U cjops -i https://pypi.org/simple
        # pip uninstall k9s -y && pip install -U k9s -i https://pypi.org/simple
        os.system('twine upload --skip-existing --repository-url https://upload.pypi.org/legacy/  dist/*')

        self.status('Pull the just package')
        os.system(f"pip uninstall {package} -y && pip install {package}=={about['__version__']} -i http://pypi.caojie.site/simple --trusted-host pypi.caojie.site")

        if Path('deploy').exists():
            Path('deploy').unlink()

        sys.exit()

# 确定entry_points = {}的值
entry_points = {}
if package == "pycj":
    entry_points = {
        "console_scripts": [
            "pycj=pycj.main:app",
        ],
    }

setup(
    # 包的分发名称，使用字母、数字、_、-
    name=about['__title__'],
     # 版本号, 版本号规范：https://www.python.org/dev/peps/pep-0440/
    version=about['__version__'],
    # 作者名
    author=about['__author__'],
     # 作者邮箱
    author_email=about['__author_email__'],
    # 包的简介描述
    description=about['__description__'],
    # 包的详细介绍(一般通过加载README.md)
    long_description=long_description,
    # 和上条命令配合使用，声明加载的是markdown文件
    long_description_content_type="text/markdown",
    # 如果项目由多个文件组成，我们可以使用find_packages()自动发现所有包和子包，而不是手动列出每个包，在这种情况下，包列表将是example_pkg
    # packages=setuptools.find_packages(),
    packages=packages,  # 指定包名，确保只包含你需要的包
    package_dir={"": "src"},  # 指定包的根目录为src
    # 关于包的其他元数据(metadata)
    zip_safe=False,# 设置为False,提高安装效率和性能
    classifiers=[
         # 该软件包仅与Python3兼容
        "Programming Language :: Python :: 3",
        # 根据MIT许可证开源
        "License :: OSI Approved :: MIT License",
        # 与操作系统无关
        "Operating System :: OS Independent",
    ],
    # 依赖模块
    install_requires= require_package,
    include_package_data=True,
    python_requires='>=3',
    # setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
    entry_points=entry_points,
)
