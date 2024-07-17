import os
from enum import Enum
from typing import TypeVar, Type, Callable
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request

from afeng_tools.application_tool import settings_tools
from afeng_tools.application_tool.settings_enum import SettingsKeyEnum
from afeng_tools.fastapi_tool.common.enum import ReloadFreqEnum
from afeng_tools.fastapi_tool.core.fastapi_exception_handler import HtmlFileResponseException
from afeng_tools.fastapi_tool.fastapi_request_tools import generate_request_id
from afeng_tools.fastapi_tool.template.fastapi_template_tools import is_need_reload
from afeng_tools.pydantic_tool.model.common_models import EnumItem


def convert_enum_type(param_name: str, enum_class: Type[Enum]) -> Callable:
    """
    转换枚举类型的装饰器， 使用示例：search_type: SearchTypeEnum = Depends(convert_enum_type('search_type', SearchTypeEnum)
    :param param_name: 参数名称
    :param enum_class: 枚举类型
    :return: 枚举
    """
    EnumType = TypeVar(enum_class.__name__, bound=enum_class)

    def convert_enum_type_wrapper(request: Request) -> EnumType:
        enum_type_str = request.query_params.get(param_name)
        if not enum_type_str:
            enum_type_str = request.path_params.get(param_name)
            if not enum_type_str and hasattr(request.form(), 'get'):
                enum_type_str = request.form().get(param_name)
        if enum_type_str:
            type_enum_list = [tmp for tmp in enum_class if tmp.name == enum_type_str or tmp.value == enum_type_str]
            if type_enum_list:
                return type_enum_list[0]
            else:
                type_enum_list = [tmp for tmp in enum_class if
                                  isinstance(tmp.value, EnumItem) and tmp.value.value == enum_type_str]
                if type_enum_list:
                    return type_enum_list[0]
        # raise RequestValidationError('请求参数[search_type]值有误！')

    return convert_enum_type_wrapper


def depend_cache_html_file(reload_freq: ReloadFreqEnum = ReloadFreqEnum.daily,
                           cache_path: str = None) -> Callable:
    """
    依赖（缓存html文件）
    :param reload_freq:
    :param cache_path: 缓存路径
    :return:
    """

    async def func_wrap(request: Request) -> str | None:
        if settings_tools.get_config('app.is_debug'):
            return None
        cache_dir = cache_path
        request_id = generate_request_id(request)
        if cache_dir is None:
            cache_dir = os.path.join(settings_tools.get_config('server.html_save_path'), 'cache')
        cache_html = os.path.join(cache_dir, f'{request_id}.html')
        if os.path.exists(cache_html) and not is_need_reload(cache_html, reload_freq=reload_freq):
            raise HtmlFileResponseException(html_file=cache_html, binary_flag=True)
        return cache_html

    return func_wrap
