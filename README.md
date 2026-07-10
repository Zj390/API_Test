# API Test

这是一个基于 pytest 的接口自动化测试练习项目。

项目使用 YAML 文件维护接口测试数据，使用 requests 发送 HTTP 请求，使用 pytest 管理和执行测试用例，并通过 extract.yaml 保存接口之间需要传递的临时变量，例如 access_token 和 csrf_token。

## 技术栈

- Python
- pytest
- requests
- PyYAML
- jsonpath
- pytest-html
- allure-pytest

## 项目结构

```text
api_test_git/
  commons/
    request_util.py      # HTTP 请求封装
    yaml_util.py         # YAML 文件读写工具

  testcases/
    conftest.py          # pytest fixture
    test_api.py          # 接口测试用例
    test_*.yaml          # YAML 测试数据

  extract.yaml           # 运行时临时变量，不提交到 Git
  pytest.ini             # pytest 配置文件
  requirements.txt       # 项目依赖
  run.py                 # 测试运行入口
```

## 当前已实现

- 使用 pytest 管理和执行接口测试用例
- 使用 YAML 文件维护接口测试数据
- 使用 requests.session 发送接口请求并保持会话
- 使用 extract.yaml 保存 access_token、csrf_token 等接口关联变量
- 使用 fixture 在测试开始前清空临时变量
- 使用 pytest marker 区分 smoke、user 等用例类型

## 安装依赖

如果使用 DL 环境，可以运行：

```bash
D:\Anaconda\envs\DL\python.exe -m pip install -r requirements.txt
```

## 运行测试

运行入口文件：

```bash
D:\Anaconda\envs\DL\python.exe run.py
```

或者直接运行 pytest：

```bash
D:\Anaconda\envs\DL\python.exe -m pytest
```

## 当前测试流程

1. pytest 启动测试。
2. conftest.py 中的 fixture 在测试开始前清空 extract.yaml。
3. 获取 access_token 接口执行后，将 access_token 写入 extract.yaml。
4. 查询标签、编辑标签等接口从 extract.yaml 读取 access_token。
5. 访问 phpwind 首页后，通过正则提取 csrf_token 并写入 extract.yaml。
6. 登录接口从 extract.yaml 读取 csrf_token 并完成登录请求。

## 后续优化计划

- 增加接口响应断言
- 统一请求封装，减少测试代码中的重复取值
- 支持 ${access_token}、${csrf_token} 形式的变量替换
- 增加日志记录
- 增加 HTML 或 Allure 测试报告
- 增加 CI 自动执行测试