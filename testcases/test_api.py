import pytest

from commons.case_runner import CaseRunner
from commons.yaml_util import read_all_yaml_testcases

TESTCASE_PATHS = [      # 顺序不能随便改，因为存在依赖
    "testcases/test_get_token.yaml",
    "testcases/test_select_flag.yaml",
    "testcases/test_edit_flag.yaml",
    "testcases/test_phpwind.yaml",
    "testcases/test_login.yaml",
]


def build_test_params():
    # 构建带名称和 marker 的参数
    test_params = []

    for caseinfo in read_all_yaml_testcases(TESTCASE_PATHS):
        marks = [
            getattr(pytest.mark, mark_name)
            for mark_name in caseinfo.get("marks", [])
        ]

        case_id = caseinfo["case_id"]
        depends_on = caseinfo.get("depends_on", [])

        marks.append(
            pytest.mark.dependency(
                name=case_id,
                depends=depends_on
            )
        )

        test_params.append(
            pytest.param(
                caseinfo,
                marks=marks,
                id=caseinfo["title"]
            )
        )

    return test_params
# 遍历每个用例的参数，以便后续传到测试的“caseinfo”中


class TestApi:

    @pytest.mark.parametrize(
        "caseinfo",
        build_test_params()
    )
    def test_api(self, caseinfo):
        CaseRunner.execute_case(caseinfo)
