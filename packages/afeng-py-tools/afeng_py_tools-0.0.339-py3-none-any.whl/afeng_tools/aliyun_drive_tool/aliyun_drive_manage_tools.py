from typing import List

from afeng_tools.aliyun_drive_tool.core.custom_aligo import CustomAligo
from aligo import Aligo, CreateFileResponse, MoveFileToTrashResponse, BatchSubResponse, MoveFileResponse, \
    CopyFileResponse, BaseFile
from aligo.types.Enum import CheckNameMode


def create_folder(alipan_api: Aligo, name: str,
                  parent_file_id: str = 'root', drive_id: str = None,
                  check_name_mode: CheckNameMode = 'auto_rename') -> CreateFileResponse:
    """
    创建文件夹
    :param alipan_api: Aligo
    :param name: [str] 文件夹名
    :param parent_file_id: Optional[str] 父文件夹id, 默认为 'root'
    :param drive_id: Optional[str] 指定网盘id, 默认为 None
    :param check_name_mode: Optional[CheckNameMode] 检查文件名模式, 默认为 'auto_rename'
    :return: [CreateFileResponse]
    """
    return alipan_api.create_folder(name=name,
                                    parent_file_id=parent_file_id,
                                    drive_id=drive_id,
                                    check_name_mode=check_name_mode)


def rename_file(alipan_api: Aligo, file_id: str, new_name: str,
                check_name_mode: CheckNameMode = 'refuse',
                drive_id: str = None) -> BaseFile:
    """重命名文件"""
    return alipan_api.rename_file(file_id=file_id, name=new_name, check_name_mode=check_name_mode, drive_id=drive_id)


def batch_rename_files(alipan_api: Aligo, file_id_list: List[str], new_name_list: List[str],
                       check_name_mode: CheckNameMode = 'refuse',
                       drive_id: str = None) -> List[BaseFile]:
    return alipan_api.batch_rename_files(file_id_list=file_id_list, new_name_list=new_name_list,
                                         check_name_mode=check_name_mode, drive_id=drive_id)


def copy_file(alipan_api: Aligo, file_id: str, to_parent_file_id: str = 'root', new_name: str = None,
              drive_id: str = None,
              to_drive_id: str = None) -> CopyFileResponse:
    """复制文件"""
    return alipan_api.copy_file(file_id=file_id, to_parent_file_id=to_parent_file_id, new_name=new_name,
                                drive_id=drive_id, to_drive_id=to_drive_id)


def batch_copy_file(alipan_api: Aligo, file_id_list: List[str], to_parent_file_id: str = 'root',
                    drive_id: str = None) -> List[BatchSubResponse[CopyFileResponse]]:
    """复制文件"""
    return alipan_api.batch_move_files(file_id_list=file_id_list, to_parent_file_id=to_parent_file_id,
                                       drive_id=drive_id)


def move_file(alipan_api: Aligo, file_id: str, to_parent_file_id: str = 'root', new_name: str = None,
              drive_id: str = None,
              to_drive_id: str = None) -> MoveFileResponse:
    """移动文件"""
    return alipan_api.move_file(file_id=file_id, to_parent_file_id=to_parent_file_id, new_name=new_name,
                                drive_id=drive_id, to_drive_id=to_drive_id)


def batch_move_file(alipan_api: Aligo, file_id_list: List[str], to_parent_file_id: str = 'root',
                    drive_id: str = None) -> List[BatchSubResponse[MoveFileResponse]]:
    """批量移动文件"""
    return alipan_api.batch_move_files(file_id_list=file_id_list, to_parent_file_id=to_parent_file_id,
                                       drive_id=drive_id)


def delete_file(alipan_api: CustomAligo, file_id: str, to_trash: bool = True,
                drive_id: str = None) -> MoveFileToTrashResponse | bool:
    """删除文件"""
    if to_trash:
        return alipan_api.move_file_to_trash(file_id=file_id, drive_id=drive_id)
    else:
        return alipan_api.delete_file(file_id=file_id, drive_id=drive_id)


def batch_delete_file(alipan_api: CustomAligo, file_id_list: List[str], to_trash: bool = True,
                      drive_id: str = None) -> List[BatchSubResponse]:
    """删除文件"""
    if to_trash:
        return alipan_api.batch_move_to_trash(file_id_list=file_id_list, drive_id=drive_id)
    else:
        return alipan_api.batch_delete_files(file_id_list=file_id_list, drive_id=drive_id)


def clear_recyclebin(alipan_api: CustomAligo, drive_id: str = None) -> bool:
    """清空回收站"""
    return alipan_api.clear_recyclebin(drive_id=drive_id)


if __name__ == '__main__':
    pass
