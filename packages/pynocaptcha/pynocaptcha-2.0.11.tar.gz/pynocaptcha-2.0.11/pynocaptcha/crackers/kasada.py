# -*- coding: UTF-8 -*-


from .base import BaseCracker


class KasadaCtCracker(BaseCracker):
    cracker_name = "kasada"
    cracker_version = "ct"

    """
    kasada x-kpsdk-ct cracker
    :param href: 触发验证的页面地址
    :param script_url: p.js 脚本地址
    调用示例:
    cracker = KasadaCtCracker(
        user_token="xxx",
        href="https://arcteryx.com/ca/en/shop/mens/beta-lt-jacket-7301",
        script_url="https://mcprod.arcteryx.com/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/p.js",
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        proxy="user:pass@ip:port",
        debug=True,
    )
    ret = cracker.crack()
    """

    # 必传参数
    must_check_params = ["href", "ips_url"]
    # 默认可选参数
    option_params = {
        "branch": "Master",
        "proxy": None,
        "ips_script": None,
        "ips_headers": None,
        "country": None,
        "ip": None,
        "submit": True,
        "user_agent": None,
        "timeout": 30
    }


class KasadaCdCracker(BaseCracker):
    cracker_name = "kasada"
    cracker_version = "cd"

    """
    kasada x-kpsdk-ct cracker
    :param href: 触发验证的页面地址
    调用示例:
    cracker = KasadaCdCracker(
        user_token="xxx",
        href="https://arcteryx.com/ca/en/shop/mens/beta-lt-jacket-7301",
        debug=True,
    )
    ret = cracker.crack()
    """

    # 必传参数
    must_check_params = ["href", "st"]
