import pytest

from commons.request_util import RequestUtil
from commons.yaml_util import read_all_yaml_testcases
from commons.assert_util import AssertUtil
from commons.extract_util import ExtractUtil
from commons.replace_util import ReplaceUtil

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

        test_params.append(
            pytest.param(
                caseinfo,
                marks=marks,
                id=caseinfo["title"]
            )
        )

    return test_params

class TestApi:

    @staticmethod
    def execute_case(caseinfo):
        request_data = ReplaceUtil.replace_variables(
            caseinfo["request"]
        )

        response = RequestUtil().send_all_request(
            **request_data
        )

        AssertUtil.validate_response(
            response,
            caseinfo.get("validate")
        )

        ExtractUtil.extract_and_save(
            response,
            caseinfo.get("extract")
        )

    @pytest.mark.parametrize(
        "caseinfo",
        build_test_params()
    )
    def test_api(self, caseinfo):
        self.execute_case(caseinfo)
