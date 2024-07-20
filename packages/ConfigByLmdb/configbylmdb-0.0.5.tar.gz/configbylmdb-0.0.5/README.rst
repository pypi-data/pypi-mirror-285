=============
ConfigByLmdb
=============

ConfigByLmdb 是一个基于 lmdb 1.5.1 版本 二次封装的库，主要用于快速动态读写大量配置信息的数据库工具。

概述
----

lmdb是一个轻量级、本地部署的高性能数据库，ConfigByLmdb 仅对其进行了简单的接口封装。


安装
----

使用 pip 安装 ConfigByLmdb ：

.. code-block:: bash

    pip install ConfigByLmdb

请注意，由于本项目是 lmdb 的二次封装版本，可能需要从源代码安装或使用特定的安装步骤。

使用示例
--------

以下是一个简单的使用示例，展示如何使用：

.. code-block:: python

    from ConfigByLmdb import DB

    # 操作键方法
    # write
    # read
    # delete
    # updata

    # 操作内部 json 方法
    # get
    # set
    # remove

    # 分页获取方法
    # get_sum
    # get_limit

    db = DB()
    # 键操作
    db.write('a',{'a':1,'b':{'c':2,'d':{"e":{"f":123,"g":None}}}})
    print(db.read('a'))
    # 内部 json 操作
    print(db.remove(['a','b','d','e','f']))
    print(db.get(['a']))
    # 分页获取
    print(db.get_sum())
    print(len(db.get_limit(1000,100).keys()))
    # 删除数据库
    DB.cleanup()

贡献
----

我们欢迎任何形式的贡献，包括但不限于：

- 报告问题或错误。
- 提供功能请求或改进建议。

许可证
------

本项目采用 OLDAP-2.8 许可证。有关更多信息，请查看 `LICENSE` 文件。
