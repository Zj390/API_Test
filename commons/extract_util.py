import re
from commons.yaml_util import write_yaml


class ExtractUtil:

    @staticmethod
    def extract_and_save(response, extract):
        if not extract:
            return

        assert isinstance(extract, dict), (
            f"extract必须是字典：{type(extract).__name__}"
        )

        extracted_values = {}

        for variable_name, rule in extract.items():
            assert isinstance(rule, dict), (
                f"{variable_name}的提取规则必须是字典"
            )

            source = rule.get("source")

            assert source in ("json", "text"), (
                f"不支持的提取来源：{source}"
            )

            if source == "json":
                body = response.json()

                assert isinstance(body, dict), (
                    f"json响应不是字典：{body}"
                )

                field = rule.get("field")

                assert field, (         # YAML有没有告诉程序提取哪个字段
                    f"{variable_name}缺少field配置"
                )

                assert field in body, (     # 判断接口响应中有没有这个字段
                    f"响应中不存在待提取字段：{field},"
                    f"实际响应：{body}"
                )

                value = body[field]

            else:
                pattern = rule.get("regex")
                group = rule.get("group", 1)

                assert pattern, (
                    f"{variable_name}缺少regex配置"
                )

                assert isinstance(group, int) and group >= 0, (
                    f"{variable_name}的group必须是非负整数，"
                    f"实际是：{group}"
                )

                try:
                    result = re.search(pattern, response.text)
                except re.error as error:
                    raise AssertionError(
                        f"{variable_name}正则表达式不合法：{error}"
                    ) from error

                assert result is not None, (
                    f"正则表达式没有匹配到内容：{pattern}"
                )

                try:
                    value = result.group(group)
                except IndexError as error:
                    raise AssertionError(
                        f"{variable_name}不存在正则分组：{group}"
                    ) from error

            assert value not in (None, {}, [], ""), (
                f"提取结果不能为空：{variable_name}"
            )

            extracted_values[variable_name] = value     # 这里保存下每个需要提取的键值对

        write_yaml(extracted_values)