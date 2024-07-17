"""
用户工具
pip install aligo -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""
from typing import Literal

from aligo import Aligo, BaseUser, BaseDrive


def get_user_info(alipan_api: Aligo) -> BaseUser:
    """获取用户信息"""
    return alipan_api.get_user()


def get_drive(alipan_api: Aligo,
              drive_name: Literal[
                  'resource', 'sharedAlbum', 'alibum', 'note_drive', 'Default'] = 'Default', ) -> BaseDrive:
    drive_list = alipan_api.list_my_drives()
    for tmp_driver in drive_list:
        if drive_name == 'Default':
            if tmp_driver.drive_id == alipan_api.get_user().default_drive_id:
                return tmp_driver
        elif tmp_driver.drive_name == drive_name:
            return tmp_driver


def get_resource_drive(alipan_api: Aligo) -> BaseDrive:
    """获取资源盘"""
    return get_drive(alipan_api, drive_name='resource')


def get_resource_drive_id(alipan_api: Aligo) -> str:
    """获取资源盘id"""
    return alipan_api.v2_user_get().resource_drive_id


def get_default_drive(alipan_api: Aligo) -> BaseDrive:
    """获取默认盘"""
    return get_drive(alipan_api, drive_name='Default')
