import os
from typing import List, Optional, Callable, Union

from aligo import Aligo, BaseFile, BatchSubResponse, FolderSizeInfo, CreateFileResponse, GetFilePathResponse
from aligo.types.Enum import CheckNameMode

from .core import alipan_file_tools


def get_folder_size_info(alipan_api: Aligo, file_id: str, drive_id: str = None) -> FolderSizeInfo:
    """获取文件夹大小信息"""
    return alipan_api.get_folder_size_info(file_id=file_id, drive_id=drive_id)


def get_file(alipan_api: Aligo, file_id: str, drive_id: str = None) -> BaseFile:
    """获取文件信息"""
    return alipan_api.get_file(file_id=file_id, drive_id=drive_id)


def get_file_path(alipan_api: Aligo, file_id: str, drive_id: str = None) -> List[BaseFile]:
    """
    获取文件路径
    :param alipan_api:
    :param file_id:
    :param drive_id:
    :return: 路径从底层到高层的列表，如：/cache/afeng/test/tmp.png 返回路径的顺序是：[test, afeng, cache]
    """
    resp = alipan_api.get_path(file_id=file_id, drive_id=drive_id)
    if isinstance(resp, GetFilePathResponse):
        return resp.items


def get_file_list(alipan_api: Aligo, parent_file_id: str = 'root',
                  drive_id: str = None, parent_path: str = '/',
                  is_recursion: bool = False, recursion_deep: int = 999999999) -> List[BaseFile]:
    """列出路径下的文件"""
    result_file_list = alipan_api.get_file_list(parent_file_id=parent_file_id, drive_id=drive_id)
    if is_recursion and recursion_deep > 0:
        for tmp_file in result_file_list:
            tmp_file.path = f'/{parent_path.removeprefix("/").removesuffix("/")}/{tmp_file.name}'
            if alipan_file_tools.is_folder(tmp_file):
                child_file_list = get_file_list(alipan_api,
                                                parent_file_id=tmp_file.file_id,
                                                drive_id=drive_id,
                                                parent_path=tmp_file.path,
                                                is_recursion=is_recursion, recursion_deep=recursion_deep - 1)
                if child_file_list:
                    result_file_list.extend(child_file_list)
    else:
        for tmp_file in result_file_list:
            tmp_file.path = f'/{parent_path.removeprefix("/").removesuffix("/")}/{tmp_file.name}'
    return result_file_list


def batch_get_files(alipan_api: Aligo, file_id_list: List[str],
                    drive_id: str = None) -> List[BatchSubResponse]:
    """批量获取文件信息"""
    return alipan_api.batch_get_files(file_id_list=file_id_list, drive_id=drive_id)


def iterate_handle_all_file(alipan_api: Aligo,
                            iterate_handle_func: Callable[[Aligo, BaseFile], None],
                            parent_file_id: str = 'root',
                            parent_path: str = '/',
                            drive_id: str = None, ):
    """
    迭代处理所有文件（会递归处理所有文件）
    :param alipan_api:
    :param iterate_handle_func: 迭代处理函数， 参数（alipan_api: Aligo, share_token: GetShareTokenResponse,ali_file:BaseShareFile）
            - 如果是文件夹， 当返回值为True时，则继续向下递归，如果为false，则不再递归
    :param parent_file_id:
     :param parent_path: 上级文件路径（这个不是阿里云盘必须的，只是效仿百度网盘的路径表示方式）
     :param drive_id:
    :return:
    """

    def _file_handle(pan_path: str, pan_file: BaseFile):
        pan_file.path = f'/{pan_path.replace(os.sep, "/").removeprefix("/").removesuffix("/")}/{pan_file.name}'
        iterate_handle_func(alipan_api, pan_file)

    alipan_api.walk_files(callback=_file_handle,
                          parent_file_id=parent_file_id,
                          drive_id=drive_id,
                          _path=parent_path)


def get_file_by_path(alipan_api: Aligo, file_path: str = '/',
                     parent_file_id: str = 'root',
                     check_name_mode: CheckNameMode = 'refuse',
                     drive_id: str = None) -> Optional[BaseFile]:
    """通过路径获取文件信息"""
    return alipan_api.get_file_by_path(path=file_path,
                                       parent_file_id=parent_file_id,
                                       check_name_mode=check_name_mode, drive_id=drive_id)


def get_folder_by_path(alipan_api: Aligo, file_path: str = '/',
                       parent_file_id: str = 'root',
                       create_folder: bool = False,
                       check_name_mode: CheckNameMode = 'refuse',
                       drive_id: str = None) -> Union[BaseFile, CreateFileResponse, None]:
    """通过路径获取文件信息"""
    return alipan_api.get_folder_by_path(path=file_path,
                                         parent_file_id=parent_file_id,
                                         create_folder=create_folder,
                                         check_name_mode=check_name_mode, drive_id=drive_id)
