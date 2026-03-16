"""环境路由：根据 APPLICATION_STANDARD_ENV 选择服务域名"""

import os
from typing import Optional

AIGC_HOSTS = {
    "qa": "http://aigc-parser.qa.s.qima-inc.com",
    "pre": "http://aigc-parser.pre.s.qima-inc.com",
    "prod": "http://aigc-parser.prod.s.qima-inc.com",
}

PROXY_HOSTS = {
    "qa": "http://proxy-static-qa.s.qima-inc.com",
    "pre": "http://proxy-static-pre.s.qima-inc.com",
    "prod": "http://proxy-static-prod.s.qima-inc.com",
}


def get_aigc_host(env: Optional[str] = None) -> str:
    if env is None:
        env = os.getenv("APPLICATION_STANDARD_ENV", "qa")
    return AIGC_HOSTS.get(env) or AIGC_HOSTS["qa"]


def get_proxy_host(env: Optional[str] = None) -> str:
    if env is None:
        env = os.getenv("APPLICATION_STANDARD_ENV", "qa")
    return PROXY_HOSTS.get(env) or PROXY_HOSTS["qa"]
