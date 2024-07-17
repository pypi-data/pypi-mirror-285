from typing import Any

import requests

from afeng_tools.quark_tool.core.quark_response_items import QuarkResponse


def create_default_headers() -> dict[str, str]:
    """创建默认header"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.24',
        'Origin': 'https://pan.quark.cn',
        'Referer': 'https://pan.quark.cn',
    }


def post(url, json_params: dict[str, Any] = None) -> dict[str, Any]:
    response = requests.post(url, headers=create_default_headers(), json=json_params)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        return response.json()


def get(url) -> dict[str, Any]:
    response = requests.get(url, headers=create_default_headers())
    if response.status_code == 200:
        response.encoding = 'utf-8'
        return response.json()
