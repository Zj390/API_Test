class LogUtil:

    MASKED_VALUE = "***"

    SENSITIVE_KEYWORDS = (
        "password",
        "passwd",
        "secret",
        "token",
        "authorization",
        "cookie"
    )

    @classmethod
    def mask_sensitive_data(cls, data):
        """递归隐藏字典和列表中的敏感字段。"""
        if isinstance(data, dict):
            masked_data = {}

            for key, value in data.items():
                if cls._is_sensitive_key(key):
                    masked_data[key] = cls.MASKED_VALUE
                else:
                    masked_data[key] = cls.mask_sensitive_data(
                        value
                    )

            return masked_data

        if isinstance(data, list):
            return [
                cls.mask_sensitive_data(value)
                for value in data
            ]

        if isinstance(data, tuple):
            return tuple(
                cls.mask_sensitive_data(value)
                for value in data
            )

        return data

    @classmethod
    def _is_sensitive_key(cls, key):
        """判断字段名称是否包含敏感关键词。"""
        normalized_key = str(key).lower()

        return any(
            keyword in normalized_key
            for keyword in cls.SENSITIVE_KEYWORDS
        )