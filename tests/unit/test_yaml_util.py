import pytest

from commons import yaml_util


pytestmark = pytest.mark.unit


@pytest.fixture
def temporary_extract_file(tmp_path, monkeypatch):
    """
    为每个测试创建独立的临时 extract.yaml。

    tmp_path 由 pytest 提供；
    monkeypatch 会临时替换 YamlUtil 使用的真实文件路径。
    """
    extract_file = tmp_path / "extract.yaml"

    monkeypatch.setattr(
        yaml_util,
        "EXTRACT_FILE",
        extract_file
    )

    return extract_file


def test_write_and_read_yaml(temporary_extract_file):
    # 第一次写入两个变量。
    yaml_util.write_yaml({
        "access_token": "old-token",
        "csrf_token": "csrf-123"
    })

    # 第二次只更新 access_token。
    yaml_util.write_yaml({
        "access_token": "new-token"
    })

    # 同名变量应该被覆盖。
    assert yaml_util.read_yaml("access_token") == "new-token"

    # 未被更新的变量应该继续保留。
    assert yaml_util.read_yaml("csrf_token") == "csrf-123"


def test_clear_yaml(temporary_extract_file):
    yaml_util.write_yaml({
        "access_token": "test-token"
    })

    yaml_util.clear_yaml()

    # 清空后的 YAML 文件应该被当作空字典处理。
    assert yaml_util._read_extract_data() == {}


def test_missing_extract_file(temporary_extract_file):
    # 临时文件尚未创建时，也应该返回空字典。
    assert temporary_extract_file.exists() is False
    assert yaml_util._read_extract_data() == {}


def test_missing_variable(temporary_extract_file):
    yaml_util.write_yaml({
        "access_token": "test-token"
    })

    # 读取不存在的变量时，应明确抛出 KeyError。
    with pytest.raises(KeyError):
        yaml_util.read_yaml("missing_variable")


def test_write_yaml_requires_dictionary(temporary_extract_file):
    # extract.yaml 使用键值对保存变量，因此只接受字典。
    with pytest.raises(
        AssertionError,
        match="写入的数据必须是字典"
    ):
        yaml_util.write_yaml(["not", "a", "dictionary"])


def test_read_testcase_from_different_working_directory(
    tmp_path,
    monkeypatch
):
    # 模拟从项目目录以外的位置运行测试。
    monkeypatch.chdir(tmp_path)

    testcases = yaml_util.read_yaml_testcase(
        "testcases/test_get_token.yaml"
    )

    assert isinstance(testcases, list)
    assert len(testcases) > 0
    assert "request" in testcases[0]