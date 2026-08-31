import requests


class RequestUtil:
    DEFAULT_TIMEOUT = 10
    sess = requests.session()

    # 统一请求封装
    def send_all_request(self, **kwargs):
        # YAML 没有配置 timeout 时，使用默认值。
        # 如果 YAML 已经配置，则保留用例自己的值。
        kwargs.setdefault(
            "timeout",
            self.DEFAULT_TIMEOUT
        )

        response = RequestUtil.sess.request(**kwargs)

        print(response.text)

        return response