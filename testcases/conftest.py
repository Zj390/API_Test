import pytest

from commons.yaml_util import clear_yaml


# 专门用来存放装饰器（夹具）

# fixture(夹具)，可在函数、类、模块或整个会话前后加上想要的操作
@pytest.fixture(scope="session", autouse=True)
def connection_mysql():
    print("之前：链接数据库")
    clear_yaml()    # 在整个会话之前清空yaml
    yield
    print("之后：关闭数据库链接")