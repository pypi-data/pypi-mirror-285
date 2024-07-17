from typing import Optional

from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import _TemplateResponse
from afeng_tools.application_tool.application_models import AppInfo
from afeng_tools.fastapi_tool.common.enum import ReloadFreqEnum
from afeng_tools.fastapi_tool.fastapi_jinja2_tools import create_template_response_with_cache
from afeng_tools.fastapi_tool.fastapi_response_tools import resp_template
from afeng_tools.fastapi_tool.template.item import TemplateHtmlHeadData, TemplateShowQrcodeAreaData, \
    TemplateRedirectAreaData, AppinfoDataItem, TemplateAlertInfoAreaData
from afeng_tools.fastapi_tool.template.item import PageTemplateItem
from afeng_tools.fastapi_tool.template.service import template_render_service
from afeng_tools.http_tool import http_request_tools, http_params_tools
from afeng_tools.pydantic_tool.model.common_models import LinkItem


def render_template(request: Request, template_file: str, template_item: PageTemplateItem) -> _TemplateResponse:
    """响应模板"""
    return create_template_response_with_cache(request,
                                               template_file=template_file,
                                               context=template_item.model_dump())


def create_html_head_data(_app_info: AppInfo, is_mobile: bool, title: str, description: str = None,
                          keyword_list: list[str] = None,
                          author: str = None, favicon: str = None, origin: str = None,
                          custom_head_code_list: Optional[list[str]] = None) -> TemplateHtmlHeadData:
    """创建页面head"""
    if title is not None:
        title = f'{title}|{_app_info.title}|{_app_info.sub_title}'
    if description is None:
        description = f'{title}:{_app_info.description}'
    if keyword_list is None:
        keyword_list = [title]
        keyword_list.extend(_app_info.keywords)
    else:
        keyword_list = [tmp for tmp in keyword_list if tmp is not None]
    if author is None:
        author = 'chentiefeng'
    if favicon is None:
        favicon = '/favicon.ico'
    if origin is None:
        origin = _app_info.origin
    return TemplateHtmlHeadData(is_mobile=is_mobile, title=title, description=description,
                                keyword_list=keyword_list,
                                author=author, favicon=favicon, origin=origin, baidu_tm_id=_app_info.baidu_tm_id,
                                custom_head_code_list=custom_head_code_list)


def redirect_to(request: Request, target: str,
                app_info_item: AppinfoDataItem = AppinfoDataItem(title='阿锋之家'),
                page_title: str = '跳转中心',
                page_favicon_ico: str = '/static/image/favicon.ico',
                back_url: str = '/',
                ad_list: list[LinkItem] = None,
                template_file: str = 'common/views/redirect/index.html',
                group_code: str = 'common/redirect',
                is_redirect: bool = False,
                cache_html_file: str = None) -> _TemplateResponse:
    """重定向页面"""
    if not target:
        return RedirectResponse('/')
    if target.startswith('%2F'):
        target = http_params_tools.url_decode(target)
    is_mobile = http_request_tools.is_mobile(request.headers.get('user-agent'))
    context_data = {
        'is_mobile': is_mobile,
        'title': page_title,
        'favicon_ico': page_favicon_ico,
        'baidu_tm_id': app_info_item.baidu_tm_id,
    }
    _, area_template_file = template_render_service.get_template_redirect_area(
        group_code=group_code,
        context_data_func=lambda: TemplateRedirectAreaData(
            is_mobile=is_mobile,
            app_info=app_info_item,
            ad_list=ad_list,
            redirect_url=target,
            back_url=back_url
        ),
        reload_freq=ReloadFreqEnum.always)
    context_data['template_redirect_area'] = area_template_file
    return resp_template(request, template_file=template_file, context_data=context_data,
                         is_redirect=is_redirect, redirect_name='redirect',
                         cache_html_file=cache_html_file)


def redirect_to_qrcode_page(request: Request,
                            qrcode_image_url: str = '/static/image/qrcode/wx_of_qrcode.jpg',
                            qrcode_image_title: str = '公众号：阿锋之家',
                            message_list: list[str] = None,
                            page_title: str = '请关注公众号：阿锋之家',
                            page_favicon_ico: str = '/static/image/favicon.ico',
                            template_file: str = 'common/views/alert/index.html',
                            group_code: str = 'common/show_qrcode',
                            is_redirect: bool = False,
                            cache_html_file: str = None,
                            baidu_tm_id: str = None) -> _TemplateResponse:
    """重定向到扫码页"""
    is_mobile = http_request_tools.is_mobile(request.headers.get('user-agent'))
    context_data = {
        'is_mobile': is_mobile,
        'title': page_title,
        'favicon_ico': page_favicon_ico,
        'baidu_tm_id': baidu_tm_id,
    }
    if message_list is None:
        message_list = [
            '1、打开微信',
            '2、扫描上方二维码',
            '3、关注"阿锋之家"',
        ]
    _, area_template_file = template_render_service.get_template_show_qrcode_area(
        group_code=group_code,
        context_data_func=lambda: TemplateShowQrcodeAreaData(
            is_mobile=is_mobile,
            qrcode_image_url=qrcode_image_url,
            qrcode_image_title=qrcode_image_title,
            message_list=message_list
        ),
        reload_freq=ReloadFreqEnum.always)
    context_data['template_alert_area'] = area_template_file
    return resp_template(request, template_file=template_file, context_data=context_data,
                         is_redirect=is_redirect, redirect_name='qrcode',
                         cache_html_file=cache_html_file)


def redirect_to_alert_page(request: Request,
                           alert_title: str,
                           alert_message_list: list[str],
                           alert_logo_url: str = None,
                           page_title: str = None,
                           page_favicon_ico: str = '/static/image/favicon.ico',
                           template_file: str = 'common/views/alert/index.html',
                           group_code: str = 'common/alert/alert_info',
                           is_redirect: bool = False,
                           cache_html_file: str = None,
                           baidu_tm_id: str = None) -> _TemplateResponse:
    """重定向到警告页"""
    is_mobile = http_request_tools.is_mobile(request.headers.get('user-agent'))

    context_data = {
        'is_mobile': is_mobile,
        'title': page_title if page_title else alert_title,
        'favicon_ico': page_favicon_ico,
        'baidu_tm_id': baidu_tm_id,
    }
    _, area_template_file = template_render_service.get_template_alert_info_area(
        group_code=group_code,
        context_data_func=lambda: TemplateAlertInfoAreaData(
            is_mobile=is_mobile,
            alert_logo_url=alert_logo_url if alert_logo_url else TemplateAlertInfoAreaData.model_fields.get(
                'alert_logo_url').default,
            alert_title=alert_title,
            alert_message_list=alert_message_list
        ),
        reload_freq=ReloadFreqEnum.always)
    context_data['template_alert_area'] = area_template_file
    return resp_template(request, template_file=template_file, context_data=context_data,
                         is_redirect=is_redirect, redirect_name='alert',
                         cache_html_file=cache_html_file)
