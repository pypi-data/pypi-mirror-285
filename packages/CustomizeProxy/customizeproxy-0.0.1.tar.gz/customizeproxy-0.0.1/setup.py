from distutils.core import setup
from setuptools import find_packages
import sys

with open("README.rst", "r",encoding="utf-8") as f:
  long_description = f.read()

with open("LICENSE", "r",encoding="utf-8") as f:
  license = f.read()

# 定义依赖项
install_requires = [
    'mitmproxy'
]


setup(name='CustomizeProxy',  # 包名
      version='0.0.1',  # 版本号
      description='这是一个 mitmproxy 二次封装版本',
      long_description=long_description,
      long_description_content_type='text/x-rst',
      author='CC',
      author_email='3204604858@qq.com',
      url='https://github.com/mitmproxy/mitmproxy/',
      install_requires=install_requires,
      license=license,
      package_data={},
      include_package_data=True,  # 确保package_data中的模式被包含
      packages= find_packages() + ['CustomizeProxy'],
      platforms=['Windows'],
      classifiers=[
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Topic :: Software Development :: Libraries',
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Software Development :: User Interfaces"
      ],
      keywords=['CustomizeProxy'],
      python_requires=">=3.10"
      )
