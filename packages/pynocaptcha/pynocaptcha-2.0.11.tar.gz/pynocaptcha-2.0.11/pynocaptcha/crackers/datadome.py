# -*- coding: UTF-8 -*-


from .base import BaseCracker


class DatadomeCracker(BaseCracker):
    cracker_name = "datadome"
    cracker_version = "universal"

    """
    datadome
    :param href: 触发验证的页面地址
    调用示例:
    cracker = KasadaCtCracker(
        user_token="xxx",
        href="https://rendezvousparis.hermes.com/client/register",
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        proxy="user:pass@ip:port",
        debug=True,
    )
    ret = cracker.crack()
    """

    # 必传参数
    must_check_params = ["href", "proxy"]
    # 默认可选参数
    option_params = {
        "branch": "Master",
        "captcha_url": None,
        "js_url": None,
        "js_key": None,
        "did": None,
        "user_agent": None,
        "interstitial": False,
        "html": False,
        "timeout": 30
    }
