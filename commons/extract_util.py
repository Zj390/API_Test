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
                # text来源下一步再实现
                raise NotImplementedError("暂未实现text提取")

            assert value not in (None, {}, [], ""), (
                f"提取结果不能为空：{variable_name}"
            )

            extracted_values[variable_name] = value     # 这里保存下每个需要提取的键值对

        write_yaml(extracted_values)