import logging

import requests

from commons.log_util import LogUtil


logger = logging.getLogger(__name__)


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

        # 生成日志专用副本，不修改真正发送的请求参数。
        safe_request_data = LogUtil.mask_sensitive_data(
            kwargs
        )

        # URL 如果直接携带查询参数，则不在日志中显示查询部分。
        request_url = safe_request_data.get("url")

        if isinstance(request_url, str):
            safe_request_data["url"] = request_url.split(
                "?",
                1
            )[0]

        logger.info(
            "发送请求：%s",
            safe_request_data
        )

        try:
            response = RequestUtil.sess.request(**kwargs)
        except requests.RequestException as error:
            # 只记录异常类型，避免异常文本携带敏感URL。
            logger.error(
                "请求失败：%s",
                type(error).__name__
            )
            raise

        # 不记录 response.text，响应内容可能包含token。
        logger.info(
            "收到响应：status_code=%s",
            response.status_code
        )

        return response