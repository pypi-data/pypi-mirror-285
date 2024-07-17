"""
阿里云盘文件搜索工具
"""
from typing import List

from aligo import Aligo, BaseFile
from aligo.types.Enum import BaseFileCategory, SearchCategory


def search_aims(alipan_api: Aligo, keyword: str, category: BaseFileCategory = 'image',
                drive_id: str = None) -> List[BaseFile]:
    """
    搜索目标/标签
    :param alipan_api: [必选] Aligo
    :param keyword: [必选] 搜索的关键字
    :param category: [可选] 搜索的文件类型
    :param drive_id: [可选] 搜索的文件所在的网盘
    :return: [List[BaseFile]]
    """
    return alipan_api.search_aims(keyword=keyword, category=category, drive_id=drive_id)


def search_files(alipan_api: Aligo, name: str = None, category: SearchCategory = None,
                 parent_file_id: str = 'root',
                 drive_id: str = None) -> List[BaseFile]:
    """
    搜索文件
    :param alipan_api: [必选] Aligo
    :param name: [必选] 搜索的文件名
    :param category: [可选] 搜索的文件类型
    :param parent_file_id: [可选] 搜索的文件夹id
    :param drive_id: [可选] 搜索的文件所在的网盘
    :return: [List[BaseFile]
    """
    return alipan_api.search_files(name=name, category=category, parent_file_id=parent_file_id, drive_id=drive_id)

