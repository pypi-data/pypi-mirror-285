from typing import Callable, Optional, Any

from pydantic import BaseModel
from starlette.requests import Request


class FastapiConfigItem(BaseModel):
    is_json_api: Optional[bool] = None
    # 错误404创建context_data的函数，参数：(message: str, is_mobile: bool = False)
    error404_context_data_func: Optional[Callable[[str, bool], dict]] = None
    # 错误500创建context_data的函数，参数：(message: str, is_mobile: bool = False)
    error500_context_data_func: Optional[Callable[[str, bool], dict]] = None
    # 500异常后后台工作函数，如发送邮件, async def send_email(request: Request, exception: Exception, traceback_msg: str)
    error500_background_work_func: Optional[Callable[[Request, Exception, str], None]] = None
    # 错误501创建context_data的函数，参数：(message: str, is_mobile: bool = False)
    error501_context_data_func: Optional[Callable[[str, bool], dict]] = None


class ResponseResult(BaseModel):
    """响应结果"""
    # 错误码
    error_no: int = 0
    # 提示信息
    message: Optional[str] = 'success'
    # 子消息
    sub_message: Optional[str] = None
    # 响应数据
    data: Optional[Any] = None


class ResponseTemplateResult(BaseModel):
    # 模板文件，如： f'{app_info.db_code}' + '/views/error/404.html'
    template_file: str
    # 标题
    title: str
    # 消息
    message: str
    # 上下文数据
    context_data: Optional[dict[str, Any]] = None
