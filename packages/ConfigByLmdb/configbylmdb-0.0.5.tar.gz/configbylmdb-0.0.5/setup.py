from distutils.core import setup
from setuptools import find_packages
import sys

with open("README.rst", "r",encoding="utf-8") as f:
  long_description = f.read()

with open("LICENSE", "r",encoding="utf-8") as f:
  license = f.read()

# 定义依赖项
install_requires = [
    'lmdb'
]


setup(name='ConfigByLmdb',  # 包名
      version='0.0.5',  # 版本号
      description='lmdb 二次封装库',
      long_description=long_description,
      long_description_content_type='text/x-rst',
      author='CC',
      author_email='3204604858@qq.com',
      url='https://github.com/jnwatson/py-lmdb/',
      install_requires=install_requires,
      license=license,
      package_data={},
      include_package_data=True,  # 确保package_data中的模式被包含
      packages= find_packages() + ['ConfigByLmdb'],
      platforms=['Windows'],
      classifiers=[
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Topic :: Software Development :: Libraries',
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Software Development :: User Interfaces"
      ],
      keywords=['ConfigByLmdb','ConfigDB','lmdb'],
      python_requires=">=3"
      )
