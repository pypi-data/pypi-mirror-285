"""
模块渲染服务
"""
from typing import Callable

from afeng_tools.fastapi_tool.template.template_render_service.template_render_tools import render_template_file

from afeng_tools.fastapi_tool.common.enum import ReloadFreqEnum
from afeng_tools.fastapi_tool.template.item import TemplateBreadCrumbData, \
    TemplatePaginationAreaData, TemplateLeftNavData, \
    TemplatePageFooterData, TemplateResultListData, TemplateTagListData, \
    TemplateGroupListData, TemplateFilterTypeAreaData, TemplateDayCalendarData, TemplateTabPanelData, \
    TemplateTopRankingData, TemplateRedirectDownloadAreaData, TemplateRedirectAreaData, TemplateError404AreaData, \
    TemplateError500AreaData, TemplateError501AreaData, TemplateShowQrcodeAreaData, TemplateInfoAreaData, \
    TemplateAlertInfoAreaData, HotTagAreaTemplateItem, RecentAreaTemplateItem, RankingAreaTemplateItem, \
    TemplateSliderWithTitleAreaData, FilterAllTypeAreaData, FilterSortAreaData, SearchResultAreaData
from afeng_tools.template_tool.template_decorator_tools import template_area


@template_area(file='module_html/page/bread_crumb.html')
def get_template_bread_crumb(group_code: str, context_data_func: Callable[[], TemplateBreadCrumbData],
                             app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                             is_mobile: bool = True,
                             template_file: str = None) -> str:
    """
    面包屑模板
    :param is_mobile:
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param app_code:
    :param reload_freq:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        return {
            'page_title': data.page_title,
            'data_list': data.bread_crumb_list,
        }

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile, )


@template_area(file='module_html/page/left_nav.html')
def get_template_left_nav(group_code: str, context_data_func: Callable[[], TemplateLeftNavData],
                          app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                          is_mobile: bool = True,
                          template_file: str = None) -> str:
    """
    左侧导航模板
    :param is_mobile:
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param app_code:
    :param reload_freq:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        return context_data_func().model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile, )


@template_area(file='module_html/page_footer.html')
def get_template_page_footer(group_code: str, context_data_func: Callable[[], TemplatePageFooterData],
                             app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                             is_mobile: bool = True,
                             template_file: str = None) -> str:
    """
    页面底部模板
    :param is_mobile:
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param app_code:
    :param reload_freq:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        return context_data_func().model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile, )


@template_area(file='module_html/area/ranking_area.html')
def get_template_ranking_area(group_code: str, context_data_func: Callable[[], RankingAreaTemplateItem],
                              reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                              is_mobile: bool = True,
                              app_code='common', template_file: str = None) -> str:
    """
    排行榜区域模板
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param reload_freq:
    :param is_mobile: 是否是移动端
    :param app_code: 应用编码
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile)


@template_area(file='module_html/area/recent_area.html')
def get_template_recent_area(group_code: str, context_data_func: Callable[[], RecentAreaTemplateItem],
                             reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                             is_mobile: bool = True,
                             app_code='common', template_file: str = None) -> str:
    """
    最近更新区域模板
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param reload_freq:
    :param is_mobile: 是否是移动端
    :param app_code: 应用编码
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile)


@template_area(file='module_html/area/hot_tag_area.html')
def get_template_hot_tag_area(group_code: str, context_data_func: Callable[[], HotTagAreaTemplateItem],
                              reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                              is_mobile: bool = True,
                              app_code='common', template_file: str = None) -> str:
    """
    热点标签区域模板
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param reload_freq:
    :param is_mobile: 是否是移动端
    :param app_code: 应用编码
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile)


@template_area(file='module_html/list/result_list.html')
def get_template_result_list(app_code: str, group_code: str, context_data_func: Callable[[], TemplateResultListData],
                             reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                             is_mobile: bool = True,
                             template_file: str = None) -> str:
    """
    页面底部模板
    :param is_mobile:
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param app_code:
    :param reload_freq:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        return context_data_func().model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile, )


@template_area(file='module_html/list/pagination_area.html')
def get_template_pagination_area(group_code: str, context_data_func: Callable[[], TemplatePaginationAreaData],
                                 app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                 is_mobile: bool = True,
                                 template_file: str = None) -> str:
    """结果模板"""

    def context_data_func_wrapper():
        data = context_data_func()
        if data.pre_btn and data.pre_btn.title is None:
            data.pre_btn.title = '上一页'
        if data.next_btn and data.next_btn.title is None:
            data.next_btn.title = '下一页'
        return data.model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile, )


@template_area(file='module_html/list/tag_list.html')
def get_template_tag_list(group_code: str, context_data_func: Callable[[], TemplateTagListData],
                          app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                          is_mobile: bool = True,
                          template_file: str = None) -> str:
    """
    标签列表模板
    :param is_mobile:
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param app_code:
    :param reload_freq:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        return context_data_func().model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile, )


@template_area(file='module_html/list/group_list.html')
def get_template_group_list(group_code: str, context_data_func: Callable[[], TemplateGroupListData],
                            app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                            is_mobile: bool = True,
                            template_file: str = None) -> str:
    """
    分组列表模板
    :param is_mobile:
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param app_code:
    :param reload_freq:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        return context_data_func().model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile, )


@template_area(file='module_html/list/filter_type_area.html')
def get_template_filter_type_area(group_code: str, context_data_func: Callable[[], TemplateFilterTypeAreaData],
                                  app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                  is_mobile: bool = True,
                                  template_file: str = None) -> str:
    """过滤类型模板"""

    def context_data_func_wrapper():
        return context_data_func().model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile, )


@template_area(file='module_html/list/day_calendar.html')
def get_template_day_calendar(group_code: str, context_data_func: Callable[[], TemplateDayCalendarData],
                              app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                              is_mobile: bool = True,
                              template_file: str = None) -> str:
    """结果模板"""

    def context_data_func_wrapper():
        return context_data_func().model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile, )


@template_area(file='module_html/page/tab_panel.html')
def get_template_tab_panel(group_code: str, context_data_func: Callable[[], TemplateTabPanelData],
                           app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                           is_mobile: bool = True,
                           template_file: str = None) -> str:
    """Tab面板模板"""

    def context_data_func_wrapper():
        return context_data_func().model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile, )


@template_area(file='module_html/ranking_list/top_ranking_list.html')
def get_template_top_ranking_list(group_code: str, context_data_func: Callable[[], TemplateTopRankingData],
                                  app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                  is_mobile: bool = True,
                                  template_file: str = None) -> str:
    """热点数据排行模板"""

    def context_data_func_wrapper():
        return context_data_func().model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile, )


@template_area(file='module_html/redirect/download_area.html')
def get_template_redirect_download_area(group_code: str,
                                        context_data_func: Callable[[], TemplateRedirectDownloadAreaData],
                                        app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                        is_mobile: bool = True,
                                        template_file: str = None) -> str:
    """下载区域模板"""

    def context_data_func_wrapper():
        return context_data_func().model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile, )


@template_area(file='module_html/redirect/redirect_area.html')
def get_template_redirect_area(group_code: str,
                               context_data_func: Callable[[], TemplateRedirectAreaData],
                               app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                               is_mobile: bool = True,
                               template_file: str = None) -> str:
    """下载区域模板"""

    def context_data_func_wrapper():
        return context_data_func().model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile)


@template_area(file='module_html/redirect/info_area.html')
def get_template_info_area(group_code: str,
                           context_data_func: Callable[[], TemplateInfoAreaData],
                           app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                           is_mobile: bool = True,
                           template_file: str = None) -> str:
    """信息区域模板"""

    def context_data_func_wrapper():
        return context_data_func().model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile)


@template_area(file='module_html/alert/show_qrcode_area.html')
def get_template_show_qrcode_area(group_code: str,
                                  context_data_func: Callable[[], TemplateShowQrcodeAreaData],
                                  app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                  is_mobile: bool = True,
                                  template_file: str = None) -> str:
    """显示二维码模板"""

    def context_data_func_wrapper():
        return context_data_func().model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile)


@template_area(file='module_html/alert/alert_info_area.html')
def get_template_alert_info_area(group_code: str,
                                 context_data_func: Callable[[], TemplateAlertInfoAreaData],
                                 app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                 is_mobile: bool = True,
                                 template_file: str = None) -> str:
    """警告信息区域模板"""

    def context_data_func_wrapper():
        return context_data_func().model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile)


@template_area(file='module_html/error/404_area.html')
def get_template_error_404_area(group_code: str,
                                context_data_func: Callable[[], TemplateError404AreaData],
                                app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                is_mobile: bool = True,
                                template_file: str = None) -> str:
    """404错误区域模板"""

    def context_data_func_wrapper():
        return context_data_func().model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile)


@template_area(file='module_html/error/500_area.html')
def get_template_error_500_area(group_code: str,
                                context_data_func: Callable[[], TemplateError500AreaData],
                                app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                is_mobile: bool = True,
                                template_file: str = None) -> str:
    """500错误区域模板"""

    def context_data_func_wrapper():
        return context_data_func().model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile)


@template_area(file='module_html/error/501_area.html')
def get_template_error_501_area(group_code: str,
                                context_data_func: Callable[[], TemplateError501AreaData],
                                app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                is_mobile: bool = True,
                                template_file: str = None) -> str:
    """500错误区域模板"""

    def context_data_func_wrapper():
        return context_data_func().model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile)


@template_area(file='module_html/header/slider_with_title_area.html')
def get_template_slider_with_title_area(group_code: str,
                                        context_data_func: Callable[[], TemplateSliderWithTitleAreaData],
                                        app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                        is_mobile: bool = False,
                                        template_file: str = None) -> str:
    """
    页面轮播图模板
    :param is_mobile:
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param reload_freq:
    :param app_code: app编码
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile)


@template_area(file='module_html/list/filter_all_type_area.html')
def get_template_filter_all_type_area(group_code: str, context_data_func: Callable[[], FilterAllTypeAreaData],
                                      reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                      is_mobile: bool = True,
                                      app_code: str = 'common',
                                      template_file: str = None) -> str:
    """
    过滤类型模板
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param reload_freq:
     :param is_mobile: 是否是移动端
     :param app_code: 应用编码
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile)


@template_area(file='module_html/list/filter_sort_area.html')
def get_template_filter_sort_area(group_code: str, context_data_func: Callable[[], FilterSortAreaData],
                                  reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                  is_mobile: bool = True,
                                  app_code: str = 'common',
                                  template_file: str = None) -> str:
    """
    排序类型模板
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param reload_freq:
     :param is_mobile: 是否是移动端
     :param app_code: 应用编码
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile)


@template_area(file='module_html/list/search_result_list.html')
def get_template_search_result_list(group_code: str, context_data_func: Callable[[], SearchResultAreaData],
                                    reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                    is_mobile: bool = True,
                                    app_code: str = 'common',
                                    template_file: str = None) -> str:
    """
    页面底部模板
    :param is_mobile:
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param app_code:
    :param reload_freq:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        return context_data_func().model_dump()

    return render_template_file(app_code, template_file,
                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                reload_freq=reload_freq, is_mobile=is_mobile, )
