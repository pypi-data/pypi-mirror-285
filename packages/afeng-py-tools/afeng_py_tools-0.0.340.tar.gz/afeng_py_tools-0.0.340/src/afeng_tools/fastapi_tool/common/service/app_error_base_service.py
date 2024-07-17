from abc import abstractmethod
from typing import Callable
from starlette.requests import Request
from afeng_tools.application_tool.application_models import AppInfo
from afeng_tools.fastapi_tool.common.enum import ReloadFreqEnum
from afeng_tools.fastapi_tool.common.service.error_base_service import DefaultErrorService
from afeng_tools.fastapi_tool.template import template_render_service, template_service
from afeng_tools.fastapi_tool.template.item import TemplateBreadCrumbData, Error404DataItem, Error500DataItem, \
    Error501DataItem
from afeng_tools.http_tool import http_request_tools


class DefaultAppErrorService(DefaultErrorService):
    @staticmethod
    @abstractmethod
    def get_template_page_header_func() -> Callable[[...], str]:
        """获取模板页头的函数"""
        pass

    @staticmethod
    @abstractmethod
    def get_template_page_footer_func() -> Callable[[...], str]:
        """获取模板页底部的函数"""
        pass

    @staticmethod
    @abstractmethod
    def get_app_info() -> AppInfo:
        pass

    def get_common_template_context_data(self, is_mobile: bool, error_code: int, error_title: str):
        group_code = f'error/{error_code}'
        template_tuple_list = [
            ('template_head', template_render_service.get_template_head(
                group_code=group_code,
                context_data_func=lambda: template_service.create_html_head_data(_app_info=self.get_app_info(),
                                                                                 is_mobile=is_mobile,
                                                                                 title=error_title),
                reload_freq=ReloadFreqEnum.weekly
            )),
            ('template_bread_crumb', template_render_service.get_template_bread_crumb(
                group_code=group_code,
                context_data_func=lambda: TemplateBreadCrumbData(is_mobile=is_mobile,
                                                                 page_title=error_title,
                                                                 bread_crumb_list=[]),
                reload_freq=ReloadFreqEnum.yearly
            )),
        ]
        template_page_header_func = self.get_template_page_header_func()
        if template_page_header_func:
            template_tuple_list.append(('template_page_header', template_page_header_func(is_mobile=is_mobile)))
        template_page_footer_func = self.get_template_page_footer_func()
        if template_page_footer_func:
            template_tuple_list.append(('template_page_footer', template_page_footer_func(is_mobile=is_mobile)))
        context_data = {
            'is_mobile': is_mobile,
            'title': error_title,
        }
        for template_name, template_file in template_tuple_list:
            context_data[template_name] = template_file
        return context_data

    def handle_404(self, error_data: Error404DataItem, request: Request = None, context_data: dict = None,
                   app_info: AppInfo = None):
        tmp_app_info = self.get_app_info()
        if not tmp_app_info:
            app_info = tmp_app_info
        common_context_data = self.get_common_template_context_data(
            is_mobile=http_request_tools.is_mobile(request.headers.get('user-agent')),
            error_code=404,
            error_title='404-Not Found')
        if context_data:
            common_context_data.update(context_data)
        return super().handle_404(error_data, request=request, context_data=common_context_data,
                                  app_info=app_info)

    def handle_500(self, error_data: Error500DataItem, request: Request = None, context_data: dict = None,
                   app_info: AppInfo = None):
        tmp_app_info = self.get_app_info()
        if not tmp_app_info:
            app_info = tmp_app_info
        common_context_data = self.get_common_template_context_data(
            is_mobile=http_request_tools.is_mobile(request.headers.get('user-agent')),
            error_code=500,
            error_title='500-服务器错误')
        if context_data:
            common_context_data.update(context_data)
        if not error_data.contact_info_url:
            error_data.contact_info_url = f'mailto:{app_info.contact_email}'
        return super().handle_500(error_data, request=request, context_data=common_context_data,
                                  app_info=app_info)

    def handle_501(self, error_data: Error501DataItem, request: Request = None, context_data: dict = None,
                   app_info: AppInfo = None):
        tmp_app_info = self.get_app_info()
        if not tmp_app_info:
            app_info = tmp_app_info
        common_context_data = self.get_common_template_context_data(
            is_mobile=http_request_tools.is_mobile(request.headers.get('user-agent')),
            error_code=501,
            error_title='501-操作失败')
        if context_data:
            common_context_data.update(context_data)
        if not error_data.contact_info_url:
            error_data.contact_info_url = f'mailto:{app_info.contact_email}'
        if not error_data.feedback_url:
            error_data.feedback_url = app_info.feedback_url
        return super().handle_501(error_data, request=request, context_data=common_context_data,
                                  app_info=app_info)
