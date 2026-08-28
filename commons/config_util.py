import os

from dotenv import load_dotenv

from commons.path_util import PROJECT_ROOT


ENV_FILE = PROJECT_ROOT / ".env"

# 将 .env 中的配置加载到当前 Python 进程的环境变量中。
load_dotenv(ENV_FILE)


class ConfigUtil:

    @staticmethod
    def read_env(key):
        # 根据变量名读取环境变量。
        value = os.getenv(key)

        # 缺失或为空都应该立即失败，避免把空密钥发送给接口。
        assert value not in (None, ""), (
            f"环境变量不存在或为空：{key}"
        )

        return value