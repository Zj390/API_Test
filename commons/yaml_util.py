import yaml
from commons.path_util import EXTRACT_FILE, get_project_path


def _read_extract_data():
    """读取 extract.yaml 中保存的全部临时变量。"""
    if not EXTRACT_FILE.exists():
        return {}

    with EXTRACT_FILE.open(
        encoding="utf-8",
        mode="r"
    ) as file:
        return yaml.safe_load(file) or {}


def write_yaml(data):
    """将新变量合并到 extract.yaml，并覆盖旧的同名变量。"""
    assert isinstance(data, dict), "写入的数据必须是字典"

    extract_data = _read_extract_data()
    extract_data.update(data)

    with EXTRACT_FILE.open(
            encoding="utf-8",
            mode="w"        # “w”模式会在写入前清空原文件
    ) as file:
        yaml.safe_dump(
            extract_data,
            stream=file,
            allow_unicode=True,
            sort_keys=False     # 不要让写入内容按字母排序
        )


# 从 extract.yaml 读取指定变量
def read_yaml(key):
    """读取指定的临时变量。"""
    extract_data = _read_extract_data()
    return extract_data[key]


# 清空 extract.yaml
def clear_yaml():
    """清空运行过程中保存的临时变量。"""
    EXTRACT_FILE.write_text(
        "",
        encoding="utf-8"
    )


# 从项目根目录读取测试用例
def read_yaml_testcase(yamlpath):
    testcase_path = get_project_path(yamlpath)

    with testcase_path.open(
        encoding="utf-8",
        mode="r"
    ) as file:
        value = yaml.safe_load(file)
        return value


# 按照给定顺序批量读取测试用例
def read_all_yaml_testcases(yamlpaths):
    all_testcases = []

    for yamlpath in yamlpaths:
        testcases = read_yaml_testcase(yamlpath)
        all_testcases.extend(testcases)

    return all_testcases