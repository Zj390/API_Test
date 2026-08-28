# API Test

这是一个基于 Python、pytest、requests 和 YAML 实现的接口自动化测试练习项目。

项目将请求数据、断言规则、变量提取规则和测试标记维护在 YAML 中，通过一个通用测试函数执行全部接口用例。接口之间需要传递的数据会保存到 `extract.yaml`，账号、密码和 API 密钥等本地配置通过 `.env` 管理。

## 项目目标

- 使用 YAML 管理接口测试数据，减少 Python 测试代码重复。
- 支持接口之间的动态参数传递。
- 区分 HTTP 状态、业务结果和返回数据结构断言。
- 将敏感配置与测试用例分离。
- 使用单元测试保护框架工具代码。

## 技术栈

- Python 3.11
- pytest
- requests
- PyYAML
- python-dotenv
- pytest-html
- allure-pytest

## 项目结构

```text
api_test_git/
├── commons/
│   ├── assert_util.py          # 通用响应断言
│   ├── config_util.py          # 环境变量读取
│   ├── extract_util.py         # JSON、文本响应数据提取
│   ├── path_util.py            # 项目根目录和公共文件路径
│   ├── replace_util.py         # YAML请求变量递归替换
│   ├── request_util.py         # HTTP请求统一封装
│   └── yaml_util.py            # YAML读写及批量用例加载
├── testcases/
│   ├── conftest.py             # session级fixture及临时数据清理
│   ├── test_api.py             # 通用YAML测试执行器
│   └── test_*.yaml             # 接口测试用例
├── tests/
│   └── unit/
│       ├── test_assert_util.py
│       ├── test_config_util.py
│       ├── test_extract_util.py
│       ├── test_replace_util.py
│       └── test_yaml_util.py
├── .env.example                # 环境变量示例，可提交
├── extract.yaml                # 运行时临时变量，不提交
├── pytest.ini                  # pytest配置与marker声明
├── requirements.txt            # Python依赖
└── run.py                      # 测试运行入口
```

## 已实现功能

### YAML数据驱动

每条 YAML 用例可以配置：

- `feature`：所属功能模块。
- `story`：接口或业务场景。
- `title`：显示在 pytest 结果中的用例名称。
- `marks`：pytest marker，例如 `smoke`、`user`。
- `request`：直接传给 requests 的请求参数。
- `validate`：响应断言规则。
- `extract`：响应数据提取规则。

通用测试执行流程：

```text
批量读取YAML
    ↓
替换请求中的动态变量
    ↓
发送HTTP请求
    ↓
执行YAML断言
    ↓
提取并保存后续接口需要的数据
```

### 通用请求执行器

`testcases/test_api.py` 会按照指定顺序加载多个 YAML 文件，通过一个参数化测试函数执行全部用例。

YAML 中的 `request` 会转换为 Python 字典，并通过以下方式发送：

```python
request_data = ReplaceUtil.replace_variables(caseinfo["request"])
response = RequestUtil().send_all_request(**request_data)
```

因此 YAML 请求字段需要使用 requests 支持的参数名：

- `params`：URL查询参数。
- `data`：表单请求体。
- `json`：JSON请求体。
- `headers`：请求头。

### YAML断言

目前支持以下断言规则：

```yaml
validate:
  status_code: 200
  exists:
    - access_token
  not_empty:
    - access_token
  greater_than:
    expires_in: 0
  equals:
    errcode: 0
  types:
    tags: list
  text_contains:
    - csrf_token
```

`AssertUtil` 会检查不支持或误写的规则，避免 YAML 配置错误被静默忽略。

### 响应数据提取

支持从 JSON 响应字段中提取变量：

```yaml
extract:
  access_token:
    source: json
    field: access_token
```

支持使用正则表达式从 HTML 或普通文本中提取变量：

```yaml
extract:
  csrf_token:
    source: text
    regex: 'name="csrf_token" value="(.*?)"'
    group: 1
```

提取结果会写入项目根目录的 `extract.yaml`，供后续接口使用。测试会话开始前，fixture 会清空该文件。

### 动态变量替换

从 `extract.yaml` 读取接口运行过程中提取的变量：

```yaml
access_token: ${access_token}
csrf_token: ${csrf_token}
```

从本地 `.env` 读取环境变量：

```yaml
appid: ${env:WECHAT_APPID}
secret: ${env:WECHAT_SECRET}
username: ${env:PHPWIND_USERNAME}
password: ${env:PHPWIND_PASSWORD}
```

`ReplaceUtil` 会递归处理嵌套字典和列表，并返回替换后的新数据，不直接修改原始 YAML 数据。

### 路径与临时数据管理

项目使用 `pathlib.Path` 根据源码文件位置确定项目根目录，不再依赖运行时的当前工作目录。

因此无论从 `run.py`、单个测试文件还是其他目录启动测试，都能正确定位：

- `.env`
- `extract.yaml`
- `testcases/*.yaml`

写入临时变量时，会先读取原有数据，再通过 `dict.update()` 合并新变量并覆盖写回。这样同名变量会更新，其他变量仍然保留，不会在 YAML 中产生重复键。

### pytest标记

当前已注册：

- `smoke`：冒烟测试。
- `user`：用户及业务接口测试。
- `unit`：框架工具单元测试。

### 工具单元测试

当前共有 26 个单元测试：

- `ReplaceUtil`：递归替换、普通值、空变量名和环境变量替换。
- `AssertUtil`：JSON、文本、状态码、业务值和错误规则检查。
- `ExtractUtil`：JSON提取、正则提取及多种错误场景。
- `ConfigUtil`：环境变量读取及缺失变量检查。
- YAML工具：临时数据读写、同名变量覆盖、文件清空、错误参数和跨工作目录读取。

单元测试通过 monkeypatch 隔离真实的 `.env` 和 `extract.yaml`，不会访问外部接口，也不会写入真实临时数据。

## 环境配置

项目根目录提供 `.env.example`：

```dotenv
WECHAT_APPID=your_wechat_appid
WECHAT_SECRET=your_wechat_secret
PHPWIND_USERNAME=your_phpwind_username
PHPWIND_PASSWORD=your_phpwind_password
```

在本地创建 `.env`，并填写测试环境使用的配置：

```dotenv
WECHAT_APPID=your_local_value
WECHAT_SECRET=your_local_value
PHPWIND_USERNAME=your_local_value
PHPWIND_PASSWORD=your_local_value
```

`.env`、`extract.yaml`、缓存和测试报告目录均已加入 `.gitignore`。禁止将真实密码、API secret、access token 或 Cookie 提交到 Git。

## 安装依赖

项目目前使用 `DL` Conda 环境：

```powershell
D:\Anaconda\envs\DL\python.exe -m pip install -r requirements.txt
```

也可以在已经激活的 Python 环境中执行：

```powershell
python -m pip install -r requirements.txt
```

## 运行测试

### PyCharm运行配置

项目可以保存两个本地 PyCharm 运行配置，两者都运行 `run.py`：

```text
API测试：-m "smoke or user"
单元测试：-m unit
```

### 终端运行

运行全部被 pytest 收集的测试：

```powershell
python run.py
```

只运行接口测试：

```powershell
python -m pytest -m "smoke or user"
```

只运行框架单元测试：

```powershell
python -m pytest -m unit
```

只运行冒烟测试：

```powershell
python -m pytest -m smoke
```

## 当前接口流程

微信接口：

```text
从.env读取appid和secret
    ↓
获取access_token并写入extract.yaml
    ↓
查询标签
    ↓
编辑标签
```

phpwind接口：

```text
访问首页并提取csrf_token
    ↓
从.env读取用户名和密码
    ↓
提交登录表单
```

## 当前限制

- 接口用例依赖外部测试服务和网络状态。
- 部分用例依赖固定执行顺序，不能直接并行运行。
- 编辑标签用例会修改远端测试数据，目前没有自动恢复逻辑。
- 请求封装尚未统一增加超时、日志和敏感数据脱敏。
- pytest-html 和 Allure 已列入依赖，但尚未配置正式报告流程。
- 尚未配置 CI 自动执行单元测试。

## 后续计划

1. 为 HTTP 请求增加超时、日志和敏感信息脱敏。
2. 处理接口前置依赖、结果回查和测试数据恢复。
3. 生成 HTML 或 Allure 测试报告。
4. 配置 CI 自动运行单元测试。
