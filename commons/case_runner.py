from commons.assert_util import AssertUtil
from commons.extract_util import ExtractUtil
from commons.replace_util import ReplaceUtil
from commons.request_util import RequestUtil


class CaseRunner:
    """执行一个YAML用例及其前置、回查和清理步骤。"""

    @staticmethod
    def execute_step(step, variables=None):     # 负责每个步骤执行测试的完整流程
        if not step:
            return None

        assert isinstance(step, dict), (
            "用例步骤必须是字典"
        )

        # 在每个步骤真正执行前替换变量。
        step_data = ReplaceUtil.replace_variables(
            step,
            variables
        )

        request_data = step_data.get("request")

        assert isinstance(request_data, dict), (
            "用例步骤缺少request字典"
        )

        response = RequestUtil().send_all_request(
            **request_data
        )

        AssertUtil.validate_response(
            response,
            step_data.get("validate")
        )

        ExtractUtil.extract_and_save(
            response,
            step_data.get("extract")
        )

        return response

    @staticmethod
    def execute_case(caseinfo):
        assert isinstance(caseinfo, dict), (
            "caseinfo必须是字典"
        )

        variables = caseinfo.get("variables") or {}

        setup = caseinfo.get("setup")
        verify = caseinfo.get("verify")
        cleanup = caseinfo.get("cleanup")

        # setup成功后，original_tag_name才会存在。
        if setup:
            CaseRunner.execute_step(
                setup,
                variables
            )

        main_step = {       # 这里是在创建字典
            "request": caseinfo.get("request"),
            "validate": caseinfo.get("validate"),
            "extract": caseinfo.get("extract")
        }

        try:
            response = CaseRunner.execute_step(     # 没有其他步骤的，就只执行这个
                main_step,
                variables
            )

            if verify:
                CaseRunner.execute_step(
                    verify,
                    variables
                )

            return response

        finally:
            # 主请求或verify失败时也会进入finally。
            if cleanup:
                CaseRunner.execute_step(
                    cleanup,
                    variables
                )