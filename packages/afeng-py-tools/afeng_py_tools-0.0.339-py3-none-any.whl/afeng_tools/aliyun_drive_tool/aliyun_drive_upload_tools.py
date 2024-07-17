import os
from typing import List, Callable

from aligo import Aligo, CreateFileResponse, BaseFile
from aligo.types.Enum import CheckNameMode


def upload_files(alipan_api: Aligo, local_file_paths: List[str],
                 parent_file_id: str = 'root',
                 drive_id: str = None,
                 check_name_mode: CheckNameMode = "auto_rename") -> List[BaseFile]:
    """
    批量上传文件
    :param alipan_api:
    :param local_file_paths: [List[str]] 文件路径列表
    :param parent_file_id: Optional[str] 父文件夹id, 默认为 'root'
    :param drive_id: Optional[str] 指定网盘id, 默认为 None
    :param check_name_mode: Optional[CheckNameMode] 检查文件名模式, 默认为 'auto_rename'
    :return: [List[BaseFile]]
    """
    return alipan_api.upload_files(file_paths=local_file_paths,
                                   parent_file_id=parent_file_id, drive_id=drive_id,
                                   check_name_mode=check_name_mode)


def upload_folder(alipan_api: Aligo,
                  local_folder_path: str,
                  parent_file_id: str = 'root',
                  drive_id: str = None,
                  check_name_mode: CheckNameMode = "auto_rename",
                  folder_check_name_mode: CheckNameMode = 'refuse',
                  file_filter: Callable[[os.DirEntry], bool] = lambda x: False) -> List:
    """
    上传文件夹
    :param alipan_api: Aligo
    :param local_folder_path: [str] 文件夹路径
    :param parent_file_id: Optional[str] 父文件夹id, 默认为 'root'
    :param drive_id: [str] 指定网盘id, 默认为 None, 如果为 None, 则使用默认网盘
    :param check_name_mode: [CheckNameMode] 检查文件名模式, 默认为 'auto_rename'
    :param folder_check_name_mode: [CheckNameMode] 检查文件夹名模式, 默认为 'refuse'
    :param file_filter: 文件过滤函数, 如果返回True，则忽略上册该文件
    :return: [List]
    """
    return alipan_api.upload_folder(folder_path=local_folder_path,
                                    parent_file_id=parent_file_id,
                                    drive_id=drive_id,
                                    check_name_mode=check_name_mode,
                                    folder_check_name_mode=folder_check_name_mode,
                                    file_filter=file_filter)

