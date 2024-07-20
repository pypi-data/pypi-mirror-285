import warnings

from .base import BaseCracker

warnings.filterwarnings('ignore')


class ShapeV2Cracker(BaseCracker):
    
    cracker_name = "shape"
    cracker_version = "v2"    

    """
    shape cracker
    :param href: 触发 shape 验证的首页地址
    :param user_agent: 请求流程使用 ua
    :param script_url: 加载 shape vmp 脚本的 url
    :param script_content: 加载 shape vmp 脚本内容
    :param vmp_url: shape vmp 脚本的 url
    :param vmp_content: shape vmp 脚本内容
    :param pkey: shape 加密参数名, x-xxxx-a 中的 xxxx, 如星巴克的 Dq7hy5l1-a 传  dq7hy5l1 即可
    :param request: 需要 shape 签名的接口内容
    :param fast: 是否加速计算, 默认 false （网站风控低可使用该模式）
    :param submit: 是否直接提交 request 返回响应, 默认 false
    :param return_header: submit 为 true 时返回的响应是否返回响应头 headers, 默认 false
    :param timeout: 最大破解超时时间
    调用示例:
    cracker = CloudFlareCracker(
        href=href,
        user_token="xxx",
    )
    ret = cracker.crack()
    """
    
    # 必传参数
    must_check_params = ["href", "script_url", "pkey", "request"]
    # 默认可选参数
    option_params = {
        "branch": "Master",
        "proxy": None,
        "script_content": None,
        "vmp_url": None,
        "vmp_content": None,
        "user_agent": None,
        "country": None,
        "ip": None,
        "headers": {},
        "cookies": {},
        "fast": False,
        "submit": False,
        "return_header": False,
        "timeout": 30
    }


class ShapeV1Cracker(BaseCracker):
    
    cracker_name = "shape"
    cracker_version = "v1"    

    """
    shape cracker
    :param href: 触发 shape 验证的首页地址
    :param user_agent: 请求流程使用 ua
    :param vmp_url: shape vmp 脚本的 url
    :param vmp_content: shape vmp 脚本内容
    :param timeout: 最大破解超时时间
    调用示例:
    cracker = CloudFlareCracker(
        href=href,
        user_token="xxx",
    )
    ret = cracker.crack()
    """
    
    # 必传参数
    must_check_params = ["href", "vmp_url"]
    # 默认可选参数
    option_params = {
        "branch": "Master",
        "proxy": None,
        "vmp_content": None,
        "user_agent": None,
        "country": None,
        "ip": None,
        "headers": {},
        "cookies": {},
        "fast": False,
        "timeout": 30
    }
