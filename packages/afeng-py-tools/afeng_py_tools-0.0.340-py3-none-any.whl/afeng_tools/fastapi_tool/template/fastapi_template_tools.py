"""
fastapi模板工具
"""
import os
from datetime import datetime
from typing import Callable

from afeng_tools.fastapi_tool.common.enum import ReloadFreqEnum


def is_need_reload(save_template_file: str, reload_freq: ReloadFreqEnum = ReloadFreqEnum.weekly, is_debug:bool=False) -> bool:
    """
    是否刷新模板
    :param save_template_file: 保存的模板文件
    :param reload_freq: 刷新频率
    :param is_debug: 是否是debug
    :return:
    """
    if not os.path.exists(save_template_file) or reload_freq == reload_freq.always or is_debug:
        return True
    old_update_time = os.stat(save_template_file).st_mtime
    reload_freq_item = reload_freq.value
    if reload_freq_item.judge_func and isinstance(reload_freq_item.judge_func, Callable):
        return reload_freq_item.judge_func(old_update_time)
    else:
        return (datetime.now().timestamp() - reload_freq_item.seconds_value) > old_update_time
