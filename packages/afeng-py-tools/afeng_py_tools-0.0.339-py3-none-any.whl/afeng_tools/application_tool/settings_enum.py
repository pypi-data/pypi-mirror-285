"""
- pip install pydantic -i https://pypi.tuna.tsinghua.edu.cn/simple/
"""
from enum import Enum
from typing import Optional, Any, Union

from pydantic import BaseModel


class SettingsStaticItem(BaseModel):
    """配置静态配置项"""
    # 键名
    name: Optional[str] = None
    # 访问静态资源的url前缀
    url: str
    # 静态文件的所在目录
    path: str


class SettingsKeyItem(BaseModel):
    """配置键项"""
    # 键名
    name: str
    # 值类型(默认是字符串)
    value_type: Union[type, Union[Any]] = str
    # 默认值
    default: Optional[Any] = None
    # 描述
    comment: Optional[str | list] = None
    # 是否必须有
    is_required: Optional[bool] = True


class SettingsKeyEnum(Enum):
    """应用配置枚举"""
    app_db_url = SettingsKeyItem(name='app.db_url', comment="应用数据库",  value_type=Union[str, dict])
    app_active = SettingsKeyItem(name='app.active', comment="激活使用的配置文件，多个之间使用逗号分割",
                                 value_type=Union[str, list[str]])
    app_is_debug = SettingsKeyItem(name='app.is_debug', comment="是否是调试模式", value_type=bool)
    app_is_web = SettingsKeyItem(name='app.is_web', comment="是否是web模式", value_type=bool, default=True)

    # web服务配置
    server_host = SettingsKeyItem(name='server.host', comment="服务器监听地址", value_type=str, default="127.0.0.1",
                                  is_required=False)
    server_port = SettingsKeyItem(name='server.port', comment="服务器监听端口", value_type=int, default=8081,
                                  is_required=False)
    server_origin = SettingsKeyItem(name='server.origin', comment="服务器域信息", value_type=str, is_required=False)
    server_static = SettingsKeyItem(name='server.static', comment="访问静态资源",
                                    value_type=Union[SettingsStaticItem, list[SettingsStaticItem]])
    server_template_path = SettingsKeyItem(name='server.template_path', comment="模板文件路径")

    server_static_save_path = SettingsKeyItem(name='server.static_save_path', comment="静态资源文件路径", value_type=str)

    # 日志配置
    log_info_file = SettingsKeyItem(name='log.info.file', comment="info日志文件", value_type=str,
                                    default='{tmp}/log/{date}-info.log')
    log_info_rotation = SettingsKeyItem(name='log.info.rotation', comment="info日志滚动", value_type=str,
                                        default='50 MB')
    log_error_file = SettingsKeyItem(name='log.error.file', comment="error日志文件", value_type=str,
                                     default='{tmp}/log/{date}-error.log')
    log_error_rotation = SettingsKeyItem(name='log.error.rotation', comment="error日志滚动", value_type=str,
                                         default='50 MB')
    email_login = SettingsKeyItem(name='email.login', comment="登录邮箱", value_type=str)
    email_nickname = SettingsKeyItem(name='email.nickname', comment="登录昵称", value_type=str)
    email_password = SettingsKeyItem(name='email.password', comment="登录密码", value_type=str)

    weixin_app_id = SettingsKeyItem(name='weixin.app_id', comment="微信app_id", value_type=str)
    weixin_app_secret = SettingsKeyItem(name='weixin.app_secret', comment="微信app_secret", value_type=str)
    weixin_token = SettingsKeyItem(name='weixin.token', comment="微信token", value_type=str)
    weixin_encoding_aes_key = SettingsKeyItem(name='weixin.encoding_aes_key', comment="微信encoding_aes_key", value_type=str)