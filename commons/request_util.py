import requests

class RequestUtil:

    sess = requests.session()
    # 统一请求封装
    def send_all_request(self, **kwargs):

        res = RequestUtil.sess.request(**kwargs)

        print(res.text)

        return res