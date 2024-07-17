"""
模块页面主模块渲染服务
"""
from typing import Callable

from afeng_tools.fastapi_tool.common.enum import ReloadFreqEnum
from afeng_tools.fastapi_tool.template.item import TemplateHtmlHeadData, TemplateTopBarData, TemplateLogoSearchData, \
    TemplateIndexPageHeaderData, TemplatePageSearchHeaderData, TemplatePageHeaderData, TemplateFixNavData
from afeng_tools.fastapi_tool.template.template_render_service.template_render_tools import render_template_file
from afeng_tools.template_tool.template_decorator_tools import template_area


@template_area(file='views/head/page_head.html')
def get_template_head(group_code: str, context_data_func: Callable[[], TemplateHtmlHeadData],
                      app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                      is_mobile: bool = True,
                      template_file: str = None) -> str:
    def context_data_func_wrapper():
        data = context_data_func()
        context_data = data.model_dump()
        context_data['head_title'] = data.title
        context_data['head_description'] = data.description
        context_data['head_keywords'] = ','.join([tmp for tmp in data.keyword_list if tmp])
        context_data['head_author'] = data.author
        context_data['head_favicon'] = data.favicon
        context_data['head_origin'] = data.origin
        return context_data

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile)


@template_area(file='module_html/header/top_bar.html')
def get_template_top_bar(group_code: str, context_data_func: Callable[[], TemplateTopBarData],
                         app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                         is_mobile: bool = True,
                         template_file: str = None) -> str:
    """
    页面顶部topbar模板
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param app_code
    :param reload_freq:
    :param is_mobile:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile)


@template_area(file='module_html/header/logo_search.html')
def get_template_logo_search(group_code: str, context_data_func: Callable[[], TemplateLogoSearchData],
                             app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                             is_mobile: bool = True, template_file: str = None) -> str:
    """
    页面顶部logo_search模板
    :param is_mobile:
    :param app_code:
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param reload_freq:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile)


@template_area(file='module_html/header/fix_nav.html')
def get_template_fix_nav(group_code: str, context_data_func: Callable[[], TemplateFixNavData],
                         app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                         is_mobile: bool = True, template_file: str = None) -> str:
    """
    页面顶部logo_search模板
    :param is_mobile:
    :param app_code:
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param reload_freq:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile)


@template_area(file='module_html/page/page_header.html')
def get_template_page_header(group_code: str, context_data_func: Callable[[], TemplatePageHeaderData],
                             app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                             is_mobile: bool = True, template_file: str = None) -> str:
    """
    页面顶部模板
    :param is_mobile:
    :param app_code:
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param reload_freq:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        context_data = data.model_dump()
        if 'is_mobile' not in context_data:
            context_data['is_mobile'] = data.is_mobile
        if 'template_top_bar' not in context_data and data.topbar_data:
            context_data['template_top_bar'] = get_template_top_bar(app_code=app_code, group_code=group_code,
                                                                    context_data_func=lambda: data.topbar_data,
                                                                    reload_freq=reload_freq, is_mobile=is_mobile)
        if 'template_logo_search' not in context_data and data.logo_search_data:
            context_data['template_logo_search'] = get_template_logo_search(app_code=app_code, group_code=group_code,
                                                                            context_data_func=lambda: data.logo_search_data,
                                                                            reload_freq=reload_freq,
                                                                            is_mobile=is_mobile)
        if 'template_fix_nav' not in context_data and data.fix_nav_data:
            context_data['template_fix_nav'] = get_template_fix_nav(app_code=app_code, group_code=group_code,
                                                                    context_data_func=lambda: data.fix_nav_data,
                                                                    reload_freq=reload_freq, is_mobile=is_mobile)
        return context_data

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile)


@template_area(file='module_html/page/page_index_header.html')
def get_template_index_page_header(group_code: str, context_data_func: Callable[[], TemplateIndexPageHeaderData],
                                   app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                   is_mobile: bool = True,
                                   template_file: str = None) -> str:
    """
    首页页面顶部模板
    :param app_code:
    :param is_mobile:
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param reload_freq:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile)


@template_area(file='module_html/page/page_search_header.html')
def get_template_page_search_header(group_code: str, context_data_func: Callable[[], TemplatePageSearchHeaderData],
                                    app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                    is_mobile: bool = True,
                                    template_file: str = None) -> str:
    """
    页面搜索顶部模板
    :param is_mobile:
    :param app_code:
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param reload_freq:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile)
