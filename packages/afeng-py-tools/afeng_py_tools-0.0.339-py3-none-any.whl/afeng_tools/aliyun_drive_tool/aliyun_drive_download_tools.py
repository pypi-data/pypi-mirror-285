from typing import List, Callable

from aligo import Aligo, BaseFile

from afeng_tools.datetime_tool.datetime_tools import one_minute_seconds
from .core import alipan_file_tools
from .core.custom_aligo import CustomAligo


def get_download_url(alipan_api: Aligo, file_id: str,
                     file_name: str = None,
                     expire_seconds: int = 30 * one_minute_seconds,
                     drive_id: str = None) -> str:
    """
    获取下载链接
    :param alipan_api:
    :param file_id: 文件 id
    :param file_name: 文件名
    :param expire_seconds: 下载链接有效时间, 默认为半小时（30分钟）, 允许的最大值是4小时
    :param drive_id:
    :return:
    """
    download_url_resp = alipan_api.get_download_url(file_id=file_id, file_name=file_name,
                                                    expire_sec=expire_seconds,
                                                    drive_id=drive_id)
    return download_url_resp.url


def batch_get_download_url(alipan_api: Aligo,
                           file_id_list: List[str],
                           expire_seconds: int = 30 * one_minute_seconds,
                           drive_id=None) -> dict[str, str]:
    """
    批量获取下载链接
    :param alipan_api:
    :param file_id_list:
    :param expire_seconds:
    :param drive_id:
    :return: {file_id: 下载链接}
    """
    resp_list = alipan_api.batch_download_url(file_id_list=file_id_list,
                                              expire_sec=expire_seconds,
                                              drive_id=drive_id)
    return {tmp_resp.body.file_id: tmp_resp.body.url for tmp_resp in resp_list if tmp_resp.body}


def download_folder(alipan_api: Aligo, folder_file_id: str, local_folder: str = '.',
                    drive_id: str = None,
                    file_filter: Callable[[BaseFile], bool] = lambda x: False) -> str:
    """
    下载文件夹
    :param alipan_api:
    :param folder_file_id: 文件夹 id
    :param local_folder: 本地文件夹路径, 默认为当前目录, 即下载到哪里
    :param drive_id:  文件夹所在的网盘 id
    :param file_filter: 文件过滤函数，如果返回True，则该文件不下载
    :return: 本地文件夹路径
    """
    return alipan_api.download_folder(folder_file_id=folder_file_id,
                                      local_folder=local_folder, drive_id=drive_id,
                                      file_filter=file_filter)


def download_file_by_url(alipan_api: Aligo, download_url: str, local_file_path: str) -> str:
    """
    根据下载地址下载文件
    :param alipan_api:
     :param download_url: 下载地址
    :param local_file_path: 文件路径(包含文件名)
    :return: 本地文件路径
    """
    return alipan_api.download_file(file_path=local_file_path, url=download_url)


def download_file_by_id(alipan_api: Aligo, file_id: str, local_folder: str = '.') -> str:
    """
    根据下载地址下载文件
    :param alipan_api:
     :param file_id: 文件 id
    :param local_folder: 本地文件夹路径, 默认为当前目录
    :return: 本地文件路径
    """
    return download_file(alipan_api,
                         alipan_file=alipan_api.get_file(file_id),
                         local_folder=local_folder)


def download_file_by_path(alipan_api: CustomAligo, pan_path: str = '/',
                          local_folder: str = '.',
                          parent_file_id: str = 'root') -> str:
    """
    下载文件/文件夹
    :param alipan_api: Aligo
    :param pan_path: 网盘路径(相对父文件)，如：我的资源/音乐
    :param local_folder: 本地存储路径，如：D:/阿里云盘
    :param parent_file_id: 父文件id
    :return: 本地文件路径
    """
    return download_file(alipan_api,
                         alipan_file=alipan_api.get_file_by_path(path=pan_path,
                                                                 parent_file_id=parent_file_id),
                         local_folder=local_folder)


def download_file(alipan_api: Aligo, alipan_file: BaseFile, local_folder: str = '.') -> str:
    """
    根据下载地址下载文件
    :param alipan_api:
     :param alipan_file: 文件对象
    :param local_folder: 本地文件夹路径, 默认为当前目录
    :return: 本地文件路径
    """
    if alipan_file_tools.is_folder(alipan_file):
        return download_folder(alipan_api, folder_file_id=alipan_file.file_id,
                               local_folder=local_folder, drive_id=alipan_file.drive_id)
    return alipan_api.download_file(file=alipan_file, local_folder=local_folder)



