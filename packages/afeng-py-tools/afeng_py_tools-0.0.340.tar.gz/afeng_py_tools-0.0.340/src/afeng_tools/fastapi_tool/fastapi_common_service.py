import os

from afeng_tools.application_tool import settings_tools
from afeng_tools.application_tool.application_models import AppInfo


def get_html_cache_path(app_info: AppInfo = None) -> str:
    """获取html缓存路径"""
    if app_info is None:
        return os.path.join(settings_tools.get_config('server.html_save_path'), 'cache')
    return os.path.join(settings_tools.get_config('server.html_save_path'), 'cache', app_info.code)
