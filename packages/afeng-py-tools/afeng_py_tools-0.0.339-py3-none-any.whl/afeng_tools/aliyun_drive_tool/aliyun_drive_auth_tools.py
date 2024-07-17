"""
认证工具
pip install aligo -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""
from aligo import EMailConfig, set_config_folder

from .core.custom_aligo import CustomAligo


def get_alipan_api_by_email(receive_email: str, send_email: str, send_password: str, email_host: str,
                            email_port: int) -> CustomAligo:
    """
    获取api接口：发送登录二维码到邮箱(建议将邮箱绑定到微信，这样能实时收到提醒，登录过期后也可以第一时间收到登录请求。)
    :param receive_email:  接收登录邮件的邮箱地址
    :param send_email: 发送邮件的邮箱
    :param send_password: 发送邮件的密码
    :param email_host: 发送邮件的主机
    :param email_port: 发送邮件的端口
    :return: Aligo
    """
    email_config = EMailConfig(
        email=receive_email,
        # 自配邮箱
        user=send_email,
        password=send_password,
        host=email_host,
        port=email_port,
    )
    return CustomAligo(email=email_config)


def get_alipan_api_by_web(port: int, use_aria2: bool = False) -> CustomAligo:
    """获取api接口：打开浏览器访问 http://<YOUR_IP>:<port> 网页扫码登录"""
    return CustomAligo(port=port, use_aria2=use_aria2)


def get_alipan_api(name: str = None,
                   config_path: str = None,
                   use_resource_drive: bool = False,
                   use_aria2: bool = False,
                   email: EMailConfig = None,
                   port: int = None,
                   ) -> CustomAligo:
    """
    获取api接口：第一次使用，会弹出二维码，供扫描登录
    :param name: 配置文件名，如：name='一号服务器'， 会创建 <用户目录>/.alig/一号服务器.json 配置文件
    :param config_path: 配置文件目录，默认是 <用户目录>/.alig
    :param use_resource_drive: 是否是资源盘
    :param use_aria2: 是否使用 aria2 下载
    :param email:  (可选) 邮箱配置，发送登录二维码到邮箱, 参考 EMailConfig
    :param port: (可选) 开启 http server 端口，用于网页端扫码登录. 提供此值时，将不再弹出或打印二维码
    :return:
    """
    if config_path:
        set_config_folder(config_path)
    if name:
        alipan_api = CustomAligo(name=name, use_aria2=use_aria2, email=email)
    else:
        alipan_api = CustomAligo(use_aria2=use_aria2, email=email)
    if use_resource_drive:
        alipan_api.default_drive_id = alipan_api.v2_user_get().resource_drive_id
    return alipan_api
