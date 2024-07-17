"""
用户工具
pip install aligo -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""
import os.path
import time
import traceback
from typing import List, Callable

from afeng_tools.cache_tool import cache_memory_tools
from aligo import Aligo, ShareLinkExtractCodeResponse, GetShareTokenResponse, BatchShareFileSaveToDriveResponse, \
    CreateShareLinkResponse, CancelShareLinkResponse, BatchSubResponse, ShareLinkSchema, GetShareInfoResponse, \
    BaseShareFile, GetShareLinkVideoPreviewPlayInfoResponse, BaseFile, PrivateShareResponse
from aligo.types.Enum import GetShareLinkListOrderBy, OrderDirection, SearchFileOrderBy, CheckNameMode
from loguru import logger

from .core import alipan_file_tools
from .core.custom_aligo import CustomAligo


def create_share(alipan_api: Aligo, file_id: str | list[str],
                 share_pwd: str = None,
                 expiration: str = None,
                 drive_id: str = None,
                 description: str = None) -> CreateShareLinkResponse:
    """
    创建分享
    :param alipan_api:
    :param file_id: [必选] 文件id
    :param share_pwd: [可选] 分享密码，默认：None，表示无密码
    :param expiration: [可选] 有效期，utc时间字符串：YYYY-MM-DDTHH:mm:ss.SSSZ ，如：'2021-12-01T00:00:00.000Z'
    :param drive_id: [可选] 所属网盘id
    :param description: [可选] 描述
    :return:
    """
    if isinstance(file_id, list):
        return alipan_api.share_files(file_id, share_pwd=share_pwd,
                                      expiration=expiration,
                                      drive_id=drive_id,
                                      description=description)
    return alipan_api.share_file(file_id, share_pwd=share_pwd,
                                 expiration=expiration,
                                 drive_id=drive_id,
                                 description=description)


def get_share_list(alipan_api: Aligo, order_by: GetShareLinkListOrderBy = 'created_at',
                   order_direction: OrderDirection = 'DESC',
                   include_canceled: bool = False) -> List[ShareLinkSchema]:
    """
    获取分享列表
    :param alipan_api:
    :param order_by: [可选] 排序字段，默认：created_at
        :param order_direction: [可选] 排序方向，默认：DESC
        :param include_canceled: [可选] 是否包含已取消的分享，默认：False
        :return: [List[ShareLinkSchema]]
    :return:
    """
    return alipan_api.get_share_list(order_by=order_by, order_direction=order_direction,
                                     include_canceled=include_canceled)


def cancel_share(alipan_api: Aligo, share_id: str) -> CancelShareLinkResponse:
    """取消分享"""
    return alipan_api.cancel_share(share_id)


def batch_cancel_share(alipan_api: Aligo, share_id_list: List[str]) -> List[BatchSubResponse]:
    """批量取消分享"""
    return alipan_api.batch_cancel_share(share_id_list)


def get_share_list(alipan_api: Aligo,
                   order_by: GetShareLinkListOrderBy = 'created_at',
                   order_direction: OrderDirection = 'DESC',
                   include_canceled: bool = False) -> List[ShareLinkSchema]:
    """
    获取分享列表
    :param alipan_api:
    :param order_by: [可选] 排序字段，默认：created_at
    :param order_direction: [可选] 排序方向，默认：DESC
    :param include_canceled: [可选] 是否包含已取消的分享，默认：False
    :return: [List[ShareLinkSchema]]
    :return:
    """
    return alipan_api.get_share_list(order_by=order_by,
                                     order_direction=order_direction,
                                     include_canceled=include_canceled)


def get_share_info(alipan_api: Aligo, share_id: str) -> GetShareInfoResponse:
    """
    获取分享信息
    :param alipan_api:
    :param share_id: 分享id
    :return: GetShareInfoResponse
    """
    return alipan_api.get_share_info(share_id)


def get_share_info_by_link(alipan_api: Aligo, share_msg: str) -> ShareLinkExtractCodeResponse:
    """
    通过链接获取分享信息
    :param alipan_api: Aligo
    :param share_msg: 分享信息
                如：「心灵奇旅 4K 原盘 REMUX」https://www.aliyundrive.com/s/FYoddEbsSwV
                如： https://www.aliyundrive.com/s/LkUS6BrconT/folder/62074d95b39e519f60be4f73b68ac493e9977a90
    :return: 分享信息，如：result.share_id, result.share_pwd
    """
    return alipan_api.share_link_extract_code(share_msg)


def get_share_token(alipan_api: Aligo, share_id: str, share_pwd: str = '') -> GetShareTokenResponse:
    """获取share_token"""
    return alipan_api.get_share_token(share_id, share_pwd=share_pwd)


def get_share_token_with_cache(alipan_api: Aligo, share_id: str, share_pwd: str = '',
                               cache_group_code: str = 'share_token',
                               space_value: int = 100) -> GetShareTokenResponse:
    """获取缓存的share_token"""
    token_info = cache_memory_tools.get_time_cache(cache_group_code, share_id)
    if token_info:
        add_time, share_token = token_info
        if time.time() - add_time < space_value:
            return share_token
    share_token = get_share_token(alipan_api, share_id, share_pwd=share_pwd)
    cache_memory_tools.add_time_cache(cache_group_code, share_id, share_token)
    return share_token


def get_share_file_list(alipan_api: Aligo, share_token: GetShareTokenResponse,
                        parent_file_id: str = 'root', parent_path: str = '/',
                        is_recursion: bool = False, recursion_deep: int = 999999999) -> List[BaseShareFile]:
    """
    获取分享文件列表
    :param alipan_api:
    :param share_token:
    :param parent_file_id:
     :param parent_path: 上级文件路径（这个不是阿里云盘必须的，只是效仿百度网盘的路径表示方式）
    :param is_recursion: 是否递归深入获取
    :param recursion_deep: 递归的层级，默认999999999，几乎代表无限递归了
    :return:
    """
    result_file_list = alipan_api.get_share_file_list(share_token, parent_file_id=parent_file_id)
    if is_recursion and recursion_deep > 0:
        for tmp_file in result_file_list:
            tmp_file.path = f'/{parent_path.removeprefix("/").removesuffix("/")}/{tmp_file.name}'
            if alipan_file_tools.is_folder(tmp_file):
                child_file_list = get_share_file_list(alipan_api, share_token,
                                                      parent_file_id=tmp_file.file_id,
                                                      parent_path=tmp_file.path,
                                                      is_recursion=is_recursion,
                                                      recursion_deep=recursion_deep - 1)
                if child_file_list:
                    result_file_list.extend(child_file_list)
    else:
        for tmp_file in result_file_list:
            tmp_file.path = f'/{parent_path.removeprefix("/").removesuffix("/")}/{tmp_file.name}'
    return result_file_list


def iterate_handle_share_file_list(alipan_api: Aligo, share_token: GetShareTokenResponse,
                                   iterate_handle_func: Callable[[Aligo, GetShareTokenResponse, BaseShareFile], bool],
                                   parent_file_id: str = 'root', parent_path: str = '/',
                                   is_recursion: bool = False, recursion_deep: int = 999999999):
    """
    迭代处理分享文件列表
    :param alipan_api:
    :param share_token:
    :param iterate_handle_func: 迭代处理函数， 参数（alipan_api: Aligo, share_token: GetShareTokenResponse,ali_file:BaseShareFile）
            - 如果是文件夹， 当返回值为True时，则继续向下递归，如果为false，则不再递归
    :param parent_file_id:
     :param parent_path: 上级文件路径（这个不是阿里云盘必须的，只是效仿百度网盘的路径表示方式）
    :param is_recursion: 是否递归深入获取
    :param recursion_deep: 递归的层级，默认999999999，几乎代表无限递归了
    :return:
    """
    file_list = alipan_api.get_share_file_list(share_token, parent_file_id=parent_file_id)
    if is_recursion and recursion_deep > 0:
        for tmp_file in file_list:
            tmp_file.path = f'/{parent_path.removeprefix("/").removesuffix("/")}/{tmp_file.name}'
            if iterate_handle_func(alipan_api, share_token, tmp_file):
                if alipan_file_tools.is_folder(tmp_file):
                    iterate_handle_share_file_list(alipan_api, share_token,
                                                   iterate_handle_func=iterate_handle_func,
                                                   parent_file_id=tmp_file.file_id,
                                                   parent_path=tmp_file.path,
                                                   is_recursion=is_recursion,
                                                   recursion_deep=recursion_deep - 1)
    else:
        for tmp_file in file_list:
            tmp_file.path = f'/{parent_path.removeprefix("/").removesuffix("/")}/{tmp_file.name}'
            iterate_handle_func(alipan_api, share_token, tmp_file)


def get_share_file(alipan_api: Aligo, share_token: GetShareTokenResponse, file_id: str) -> BaseShareFile:
    """获取分享文件"""
    return alipan_api.get_share_file(file_id=file_id, share_token=share_token)


def save_share_file_to_pan(alipan_api: Aligo, share_token: GetShareTokenResponse,
                           file_id: str,
                           to_parent_file_id: str = 'root',
                           new_name: str = None,
                           to_drive_id: str = None) -> List[BatchShareFileSaveToDriveResponse]:
    """
    保存分享文件到云盘
    :param alipan_api: Aligo
    :param share_token: 可以调用 get_share_token() 方法获取
    :param file_id: 文件id
    :param to_parent_file_id: 目标父文件夹id，默认为根目录
    :param new_name: 新文件名
    :param to_drive_id: 目标网盘id，默认为当前网盘
    :return:
    """
    return alipan_api.share_file_saveto_drive(file_id=file_id, share_token=share_token,
                                              to_parent_file_id=to_parent_file_id, to_drive_id=to_drive_id,
                                              new_name=new_name)


def save_share_files_to_pan(alipan_api: Aligo, share_token: GetShareTokenResponse,
                            file_id_list: List[str],
                            to_parent_file_id: str = 'root',
                            auto_rename: bool = True,
                            to_drive_id: str = None) -> List[BatchShareFileSaveToDriveResponse]:
    """
    批量保存分享文件到云盘
    :param alipan_api: Aligo
    :param share_token: 可以调用 get_share_token() 方法获取
    :param file_id_list: 文件id
    :param to_parent_file_id: 目标父文件夹id，默认为根目录
    :param auto_rename:
    :param to_drive_id: 目标网盘id，默认为当前网盘
    :return:
    """
    return alipan_api.batch_share_file_saveto_drive(file_id_list=file_id_list, share_token=share_token,
                                                    to_parent_file_id=to_parent_file_id,
                                                    auto_rename=auto_rename,
                                                    to_drive_id=to_drive_id)


def batch_save_share_file_to_pan(alipan_api: Aligo, share_token: GetShareTokenResponse,
                                 share_parent_file_id: str = 'root',
                                 to_parent_file_id: str = 'root',
                                 auto_rename: bool = True,
                                 to_drive_id: str = None) -> List[BatchShareFileSaveToDriveResponse]:
    """
    批量保存分享文件到云盘
     :param alipan_api: Aligo
    :param share_token: 可以调用 get_share_token() 方法获取
    :param share_parent_file_id:
    :param to_parent_file_id:
    :param auto_rename:
    :param to_drive_id:

    :return: List[BatchShareFileSaveToDriveResponse]
    """
    # 如果遇到分享文件非常多，此段代码运行完成后，不会立马看到所有文件，可能需要几个小时才能陆续保存完成
    # 在网页保存需要几个小时，用这个一下就可以了，阿里云服务器会处理，不用等待
    return alipan_api.share_file_save_all_to_drive(share_token,
                                                   to_parent_file_id=to_parent_file_id,
                                                   parent_file_id=share_parent_file_id,
                                                   auto_rename=auto_rename,
                                                   to_drive_id=to_drive_id)


def search_share_files(alipan_api: Aligo, share_token: GetShareTokenResponse, keyword: str,
                       order_by: SearchFileOrderBy = 'name',
                       order_direction: OrderDirection = 'DESC') -> List[BaseShareFile]:
    """
    在分享中搜索文件
    :param alipan_api:
    :param share_token:
    :param keyword:
    :param order_by:
    :param order_direction:
    :return:
    """
    return alipan_api.search_share_files(keyword=keyword, share_token=share_token,
                                         order_by=order_by, order_direction=order_direction)


def download_share_file(alipan_api: CustomAligo, share_token: GetShareTokenResponse,
                        share_file: BaseShareFile,
                        local_folder: str = '.') -> str:
    """
    下载分享文件
    :param alipan_api:
    :param share_token:
    :param share_file:
    :param local_folder:
    :return:
    """
    if alipan_file_tools.is_folder(share_file):
        local_folder = os.path.join(local_folder, share_file.name)

        tmp_file_list = get_share_file_list(alipan_api, share_token, parent_file_id=share_file.file_id,
                                            is_recursion=False)
        if tmp_file_list:
            for tmp_file in tmp_file_list:
                download_share_file(alipan_api, share_token, share_file=tmp_file,
                                    local_folder=local_folder)
        return local_folder
    else:
        if share_token is None:
            share_token = get_share_token_with_cache(alipan_api, share_file.share_id)
        cache_folder_file = alipan_api.get_folder_by_path(path='/cache', create_folder=True)
        save_result = alipan_api.share_file_saveto_drive(file_id=share_file.file_id,
                                                         share_token=share_token,
                                                         to_parent_file_id=cache_folder_file.file_id)
        if hasattr(save_result, 'message'):
            raise Exception(save_result.message)
        pan_file_id = save_result.file_id
        share_file.pan_file_id = pan_file_id
        download_resp = alipan_api.get_download_url(file_id=save_result.file_id)
        share_file.md5 = download_resp.content_hash
        share_file.url = download_resp.url
        share_file.download_url = download_resp.url
        download_url = download_resp.url
        try:
            os.makedirs(local_folder, exist_ok=True)
            local_file = os.path.join(local_folder, share_file.name)
            local_file = alipan_api.download_file(file_path=local_file, url=download_url)
            if os.path.exists(local_file):
                if os.stat(local_file).st_size == 350:
                    os.remove(local_file)
                    download_url = alipan_api.get_download_url(file_id=pan_file_id)
                    local_file = alipan_api.download_file(file_path=local_file, url=download_url)
                return local_file
        except Exception as ex:
            logger.error(f'{ex}\n {traceback.format_exc()}')
        finally:
            alipan_api.delete_file(file_id=pan_file_id)


def create_private_share_file(alipan_api: Aligo, file_id: str, drive_id: str = None) -> PrivateShareResponse:
    """APP 中的快传，有效期 24 小时，只能一个人保存"""
    return alipan_api.private_share_file(file_id, drive_id=drive_id)


def create_private_share_files(alipan_api: Aligo, file_id_list: List[str],
                               drive_id: str = None) -> PrivateShareResponse:
    return alipan_api.private_share_files(file_id_list, drive_id=drive_id)


def get_share_link_video_preview_play_info(alipan_api: Aligo, share_token: GetShareTokenResponse,
                                           video_file_id: str,
                                           drive_id: str) -> GetShareLinkVideoPreviewPlayInfoResponse:
    return alipan_api.get_share_link_video_preview_play_info(file_id=video_file_id,
                                                             drive_id=drive_id,
                                                             x_share_token=share_token)


def create_aligo_file_share(alipan_api: Aligo, file: BaseFile) -> str:
    """创建Aligo文件分享"""
    return alipan_api.share_file_by_aligo(file)


def create_aligo_files_share(alipan_api: Aligo, files: List[BaseFile]) -> str:
    """创建Aligo文件分享"""
    return alipan_api.share_files_by_aligo(files)


def create_aligo_folder_share(alipan_api: Aligo, file_id: str) -> str:
    """创建Aligo文件夹分享"""
    return alipan_api.share_folder_by_aligo(file_id)


def save_aligo_share(alipan_api: Aligo, aligo_share_data: str) -> list:
    """保存Aligo分享"""
    return alipan_api.save_files_by_aligo(aligo_share_data)
