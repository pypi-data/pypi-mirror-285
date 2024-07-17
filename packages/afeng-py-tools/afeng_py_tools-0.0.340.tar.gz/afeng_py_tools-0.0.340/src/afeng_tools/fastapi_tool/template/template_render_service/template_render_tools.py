"""
模块渲染工具
"""
import os
from typing import Callable

from afeng_tools.application_tool import settings_tools
from afeng_tools.application_tool.settings_enum import SettingsKeyEnum
from afeng_tools.fastapi_tool.common.enum import ReloadFreqEnum
from afeng_tools.fastapi_tool.template import fastapi_template_tools
from afeng_tools.http_tool.http_url_tool import join_local_url
from afeng_tools.jinja2_tool import jinja2_tools

template_directory = settings_tools.get_config(SettingsKeyEnum.server_template_path)
template_env = jinja2_tools.create_template_env(directory_list=[template_directory])
is_debug = settings_tools.get_config('app.is_debug')


def render(do_render_func: Callable, **kwargs) -> str:
    """渲染"""
    return do_render_func(**kwargs)


def render_template_file(app_code: str, template_file: str, group_code: str,
                         context_data_func: Callable,
                         reload_freq: ReloadFreqEnum = ReloadFreqEnum.weekly,
                         is_mobile: bool = True,
                         **kwargs) -> str:
    """渲染模板文件"""

    template_html_file = join_local_url([app_code, template_file])
    tmp_save_html_file = join_local_url(['tmp', app_code, group_code, 'mobile' if is_mobile else 'pc', template_file])
    save_template_file = str(os.path.join(template_directory, tmp_save_html_file.removeprefix('/')))
    if fastapi_template_tools.is_need_reload(save_template_file, reload_freq, is_debug=is_debug):
        if kwargs:
            context_data = context_data_func(**kwargs)
        else:
            context_data = context_data_func()
        template_content = jinja2_tools.format_template(template_html_file, context=context_data, env=template_env)
        os.makedirs(os.path.dirname(save_template_file), exist_ok=True)
        with open(save_template_file, 'w', encoding='utf-8') as f:
            f.write('{% raw %}' + template_content + '{% endraw %}')
    return tmp_save_html_file
