class AssertUtil:

    @staticmethod
    def validate_response(response, validate):
        if not validate:
            return

        expected_status = validate.get("status_code")
        if expected_status is not None:
            assert response.status_code == expected_status, (
                f"HTTP状态码错误，预期：{expected_status}"
                f"实际：{response.status_code}"
            )

        body = response.json()

        for field in validate.get("exists", []):
            assert field in body, f"响应中缺少字段：{field}, 实际响应：{body}"

        for field in validate.get("not_empty", []):
            assert body.get(field), f"字段不能为空：{field},实际响应：{body}"

        for field, expected in validate.get("greater_than", {}).items():
            actual = body.get(field)
            assert actual is not None, f"缺少响应字段：{field}"
            assert actual > expected, f"{field}应大于{expected},实际为：{actual}"