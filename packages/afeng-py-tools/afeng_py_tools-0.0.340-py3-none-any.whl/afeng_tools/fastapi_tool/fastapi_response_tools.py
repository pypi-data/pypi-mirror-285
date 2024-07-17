import json
import os.path
from typing import Any, Optional, Mapping, Sequence

from pydantic import BaseModel
from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import FileResponse, Response, RedirectResponse, HTMLResponse, PlainTextResponse

from afeng_tools.application_tool.application_models import AppInfo
from afeng_tools.fastapi_tool.common.service import fastapi_error_service
from afeng_tools.fastapi_tool.core.fastapi_response import json_resp
from afeng_tools.fastapi_tool.fastapi_jinja2_tools import create_template_response, create_cache_template_response, \
    create_template_response_with_cache
from afeng_tools.fastapi_tool.template.item import Error404DataItem, Error501DataItem, Error500DataItem
from afeng_tools.file_tool import file_tools
from afeng_tools.http_tool import http_request_tools
from afeng_tools.sqlalchemy_tools.core.sqlalchemy_base_model import is_model_instance
from afeng_tools.sqlalchemy_tools.tool import sqlalchemy_model_tools


def resp_404(error_data: Error404DataItem, request: Request = None, context_data: dict = None,
             app_info: AppInfo = None):
    return fastapi_error_service.handle_404(error_data=error_data, request=request, context_data=context_data,
                                            app_info=app_info)


def resp_501(error_data: Error501DataItem, request: Request = None, context_data: dict = None,
             app_info: AppInfo = None):
    return fastapi_error_service.handle_501(error_data=error_data, request=request, context_data=context_data,
                                            app_info=app_info)


def resp_500(error_data: Error500DataItem, request: Request = None, context_data: dict = None,
             app_info: AppInfo = None):
    return fastapi_error_service.handle_500(error_data=error_data, request=request, context_data=context_data,
                                            app_info=app_info)


def resp_template(request: Request, template_file: str, context_data: dict[str, Any],
                  is_redirect: bool = False, redirect_name: str = None,
                  cache_html_file: str = None):
    """响应模板"""
    if is_redirect:
        return create_cache_template_response(request=request, template_file=template_file,
                                              context=context_data, cache_html_name=redirect_name)
    return create_template_response_with_cache(request=request,
                                               template_file=template_file,
                                               context=context_data,
                                               cache_html_file=cache_html_file)


def resp_json(data: Any = None, error_no: int = 0, message: str | Sequence = 'success', app_info: AppInfo = None):
    if is_model_instance(data) or (data and isinstance(data, list) and len(data) > 0 and is_model_instance(data[0])):
        data = json.loads(sqlalchemy_model_tools.to_json(data))
    if isinstance(data, BaseModel):
        data = data.model_dump(mode='json')
    return json_resp(error_no=error_no, message=message, data=data)


def resp_file(file_path: str, file_name: str = None, download_flag: bool = False,
              context_data: dict = None, app_info: AppInfo = None) -> Response:
    """响应文件"""
    if not os.path.exists(file_path):
        return resp_404(error_data=Error404DataItem(), context_data=context_data, app_info=app_info)
    response = FileResponse(file_path)
    with open(file_path, "rb") as file:
        if download_flag:
            if file_name is None:
                file_name = os.path.split(file_path)[1]
            response.headers["Content-Disposition"] = f"attachment; filename={file_name}"
        response.body = file.read()
        return response


def redirect(target_url: str, status_code: int = 307,
             headers: Optional[Mapping[str, str]] = None,
             background: Optional[BackgroundTask] = None) -> RedirectResponse:
    """重定向"""
    return RedirectResponse(target_url, status_code=status_code, headers=headers, background=background)


def resp_html_file(html_file: str, binary_flag: bool = False) -> HTMLResponse:
    """响应html文件"""
    return HTMLResponse(content=file_tools.read_file(html_file, binary_flag=binary_flag))


def resp_html(html_code: str) -> HTMLResponse:
    """响应html内容"""
    return HTMLResponse(content=html_code)


def resp_text(text: str) -> PlainTextResponse:
    """响应文本内容"""
    return PlainTextResponse(content=text)


def resp_not_found(request: Request, message: str = '资源'):
    """响应找不到"""
    sub_message = f'您访问的{message}不存在或已被删除！ (｡•ˇ‸ˇ•｡)'
    if http_request_tools.is_json(request.headers):
        return json_resp(error_no=404, message=sub_message, http_status=404)
    return resp_404(error_data=Error404DataItem(
        message=f'很抱歉，找不到{message}！',
        sub_message=sub_message
    ), request=request)

