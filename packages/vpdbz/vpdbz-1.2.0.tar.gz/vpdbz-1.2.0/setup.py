# 导入setuptools模块的setup和find_packages函数
from setuptools import setup, find_packages
# 导入glob模块，用于文件名模式匹配
import glob

# 使用setup函数开始配置包
setup(
    name="vpdbz",  # 包名为"vpdb"
    version="1.2.0",  # 包的版本号为1.1.0
    author="Devin zhang",  # 作者名为Devin Zhang
    author_email="devinzhang1994@gmail.com",  # 作者的电子邮件地址
    url="https://github.com/zhangkaifang/vpdb/",  # 包的主页，这里用了"Reference："前缀，可能有误，通常直接写URL
    # keywords=("pytorch", "vehicle", "ReID"),  # 包的关键字，这行被注释掉了
    description="Python debug configuration generator for vscode",  # 包的简短描述
    # scripts参数通常用于指定一些应当被安装到系统路径的脚本，使得用户可以直接在命令行中调用这些脚本。这个参数接受一个文件列表。
    scripts=glob.glob('scripts/*'),  # 使用glob模块找出scripts目录下所有文件，并将它们作为脚本文件安装
    install_requires=["jstyleson"],  # 安装依赖，本包安装时需要安装jstyleson包
    # long_description="https://github.com/zhangkaifang/vpdb/",  # 包的长描述，这行被注释掉了
    packages=find_packages(exclude=('examples', 'examples.*')),  # 自动寻找包含的Python包，排除examples目录
)
