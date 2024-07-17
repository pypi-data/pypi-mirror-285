from enum import Enum

from afeng_tools.pydantic_tool.model.common_models import EnumItem


class ApiErrorEnum(Enum):
    hit_frequency_limit = EnumItem(value='hit_frequency_limit', title='接口请求过于频繁，注意控制',
                                   description='命中接口频控')
    no_permission_to_access = EnumItem(value='no_permission_to_access', title='没有访问的权限')
    file_does_not_exist = EnumItem(value='file_does_not_exist', title='文件不存在')
    invalid_request = EnumItem(value='invalid_request',
                               title='请求缺少某个必需参数，包含一个不支持的参数或参数值，或者格式不正确')
    invalid_client = EnumItem(value='unknown_client',
                              title='“client_id”、“client_secret”参数无效')
    invalid_grant = EnumItem(value='grant_is_revoked',
                             title='授权是是无效的',
                             description='提供的Access Grant是无效的、过期的或已撤销的，例如，Authorization Code无效(一个授权码只能使用一次)、Refresh Token无效、redirect_uri与获取Authorization Code时提供的不一致、Devie Code无效(一个设备授权码只能使用一次)等。')
    unauthorized_client = EnumItem(value='client_is_not_authorized',
                                   title='应用没有被授权')
    unsupported_grant_type = EnumItem(value='grant_type_is_not_supported',
                                      title='不支持该授权类型')
    invalid_scope = EnumItem(value='the_requested_scope_is_exceeds_the_scope_granted',
                             title='请求的“scope”参数是无效的、未知的、格式不正确的、或所请求的权限范围超过了数据拥有者所授予的权限范围')

    expired_token = EnumItem(value='expired_token',
                             title='提供的Token已过期')
    redirect_uri_mismatch = EnumItem(value='invalid_redirect_uri',
                                     title='“redirect_uri”所在的根域与开发者注册应用时所填写的根域名不匹配')
    unsupported_response_type = EnumItem(value='the_response_type_is_not_supported',
                                         title='“response_type”参数值不支持，或者应用已经主动禁用了对应的授权模式')
    slow_down = EnumItem(value='the_request_is_polling_too_frequently',
                         title='Device Flow中，换取Access Token的接口过于频繁，两次尝试的间隔应大于5秒。')
    authorization_pending = EnumItem(value='user_has_not_yet_completed_the_authorization',
                                     title='用户还没有对Device Code完成授权操作。')
    authorization_declined = EnumItem(value='user_has_declined_the_authorization',
                                      title='用户拒绝了对Device Code的授权操作。')
    unknown_error = EnumItem(value='unknown_error',
                             title='未知错误，如果频繁发生此错误，请联系管理员')
    service_temporarily_unavailable = EnumItem(value='service_temporarily_unavailable',
                                               title='服务暂时不可用')
    unsupported_openapi_method = EnumItem(value='unsupported_openapi_method',
                                          title='访问URL错误，该接口不能访问')
    request_limit_reached = EnumItem(value='open_api_request_limit_reached',
                                     title='访问该接口的QPS达到上限')
    unauthorized_client_ip_address = EnumItem(value='unauthorized_client_ip_address',
                                              title='访问的客户端IP不在白名单内')
    daily_request_limit_reached = EnumItem(value='open_api_daily_request_limit_reached',
                                           title='访问该接口超过每天的访问限额')
    qps_request_limit_reached = EnumItem(value='open_api_qps_request_limit_reached',
                                         title='访问该接口超过QPS限额')
    total_request_limit_reached = EnumItem(value='open_api_total_request_limit_reached',
                                           title='访问该接口超过总量限额')
    invalid_parameter = EnumItem(value='invalid_parameter',
                                 title='没有获取到合法参数')
    access_token_invalid = EnumItem(value='access_token_invalid_or_no_longer_valid',
                                    title='token不合法')
    access_token_expired = EnumItem(value='access_token_expired',
                                    title='token已过期')
    no_permission_to_access_user_mobile = EnumItem(value='no_permission_to_access_user_mobile',
                                                   title='没有权限获取用户手机号')
