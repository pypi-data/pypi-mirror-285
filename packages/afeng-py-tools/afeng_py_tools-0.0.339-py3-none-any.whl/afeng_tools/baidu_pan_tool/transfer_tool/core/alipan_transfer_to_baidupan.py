import os
from typing import Callable

from aligo import Aligo, BaseShareFile, BaseFile

from afeng_tools.aliyun_pan_tool import aliyun_pan_tools
from afeng_tools.aliyun_pan_tool.aliyun_pan_share_tools import get_share_cache_token
from afeng_tools.baidu_pan_tool.core.baidu_pan_models import UploadCreateResult, FileInfo
from afeng_tools.baidu_pan_tool.tools import baidu_pan_file_upload_tools, baidu_pan_file_meta_tools, \
    baidu_pan_file_path_tools
from afeng_tools.encryption_tool import hashlib_tools
from afeng_tools.log_tool.loguru_tools import get_logger, log_error
from afeng_tools.os_tool import os_tools

logger = get_logger()


def get_baidupan_old_file_list(baidupan_access_token: str, pan_path: str,
                               interval_seconds: float = 20) -> dict[str, FileInfo]:
    """
    获取百度网盘旧文件列表
    :param baidupan_access_token:
    :param pan_path: 网盘路径
    :return: [(文件路径，文件大小)，(文件路径，文件大小)]
    :param interval_seconds: 间隔秒数，递归查询太过频繁请求接口会报错，这里是两次请求的间隔秒数
    """
    pan_path = baidu_pan_file_path_tools.parse_pan_path(pan_path)
    old_file_list = baidu_pan_file_path_tools.list_all_file(baidupan_access_token, pan_path, recursion=1,
                                                            only_file=True, interval_seconds=interval_seconds)
    if old_file_list:
        return {tmp.path: tmp for tmp in old_file_list}


def get_baidupan_save_path(alipan_path: str, baidupan_save_path_func: Callable[[str, str], str]) -> str:
    """获取百度网盘保存路径"""
    if '/' in alipan_path:
        alipan_path_info_arr = alipan_path.rsplit('/', maxsplit=1)
        alipan_parent_path, alipan_file_name = '/' + alipan_path_info_arr[0].removeprefix('/'), alipan_path_info_arr[1]
    else:
        alipan_parent_path, alipan_file_name = '/', alipan_path
    return baidupan_save_path_func(alipan_parent_path, alipan_file_name)


def init_file_md5(alipan_api: Aligo, alipan_file: BaseShareFile | BaseFile):
    if alipan_file.type == 'folder':
        return
    if not hasattr(alipan_file, 'md5') or not getattr(alipan_file, 'md5'):
        share_token = get_share_cache_token(alipan_api, alipan_file.share_id)
        save_result = alipan_api.share_file_saveto_drive(file_id=alipan_file.file_id, share_token=share_token)
        if not hasattr(save_result, 'message'):
            ali_pan_file = alipan_api.get_file(file_id=save_result.file_id)
            alipan_file.md5 = ali_pan_file.content_hash
            alipan_api.delete_file(file_id=save_result.file_id)


def alipan_file_save(baidupan_access_token: str, alipan_api: Aligo, alipan_path: str,
                     alipan_file: BaseShareFile | BaseFile,
                     transfer_list_file: str,
                     exist_file_list: list[str],
                     alipan_file_filter_func: Callable[[Aligo, str, BaseShareFile | BaseFile], bool] = lambda a, x,
                                                                                                              y: True,
                     baidupan_save_path_func: Callable[[str, str], str] =
                     lambda x, y: f'{x}/{y}',
                     baidupan_save_after_handle_func: Callable[[BaseFile, str, UploadCreateResult], None] = None,
                     is_init_file_md5: bool = True):
    """
    阿里云盘文件保存
    :param baidupan_access_token:百度网盘access_token
    :param alipan_api:
    :param alipan_path:
    :param alipan_file:
    :param transfer_list_file:
    :param exist_file_list:
    :param alipan_file_filter_func: 阿里云盘文件过滤函数，只有满足条件的文件才会进行转存，参数：(阿里云盘的路径(包含文件名): alipan_path, 阿里云盘的文件: alipan_file)-> True或False
    :param baidupan_save_path_func: 百度网盘路径函数：(阿里云盘的路径(不包含文件名，根路径为/): alipan_path, 阿里云盘的文件名: alipan_file_name)-> 百度网盘的路径
    :param baidupan_save_after_handle_func: 百度网盘保存后的处理函数，参数：(阿里云盘文件, 百度网盘保存路径（包含文件名）,上传保存结果)
    :param is_init_file_md5: 是否初始化文件的md5
    :return:
    """
    if alipan_file.file_id in exist_file_list:
        return
    if is_init_file_md5:
        init_file_md5(alipan_api=alipan_api, alipan_file=alipan_file)
    if not alipan_file_filter_func(alipan_api, alipan_path, alipan_file):
        return

    baidupan_save_path = get_baidupan_save_path(alipan_path, baidupan_save_path_func)
    try:
        old_file_info = baidu_pan_file_meta_tools.get_file_meta_by_path(baidupan_access_token, baidupan_save_path)
        if old_file_info and old_file_info.size == alipan_file.size:
            print(f'文件已经存在百度网盘：{old_file_info.path}')
            if baidupan_save_after_handle_func and isinstance(baidupan_save_after_handle_func, Callable):
                baidupan_save_after_handle_func(alipan_file, baidupan_save_path, old_file_info)
            return
        if isinstance(alipan_file, BaseShareFile):
            tmp_local_save_path = os.path.join(os_tools.get_user_home(),
                                               f'ali_tmp_file-{alipan_file.share_id}')
        else:
            tmp_local_save_path = os.path.join(os_tools.get_user_home(),
                                               f'ali_tmp_file-{hashlib_tools.calc_md5(transfer_list_file)}')
        os.makedirs(tmp_local_save_path, exist_ok=True)
        tmp_local_file = aliyun_pan_tools.download_file(alipan_api, pan_file=alipan_file,
                                                        local_path=tmp_local_save_path,
                                                        download_after_delete=isinstance(alipan_file, BaseShareFile))
        if tmp_local_file:
            result = baidu_pan_file_upload_tools.upload_file(baidupan_access_token,
                                                             local_file=tmp_local_file,
                                                             pan_path=baidupan_save_path)
            if result and result.errno == 0:
                if os.path.exists(tmp_local_file):
                    os.remove(tmp_local_file)
                with open(transfer_list_file, 'a+', encoding='utf-8') as f:
                    f.write(f'{alipan_file.file_id}\n')
            if baidupan_save_after_handle_func and isinstance(baidupan_save_after_handle_func, Callable):
                baidupan_save_after_handle_func(alipan_file, baidupan_save_path, result)
    except Exception as e:
        log_error(logger,

                  f'[alipan_share_to_baidupan]阿里云文件[{alipan_path}]转存到百度云[{baidupan_save_path}]出现异常', e)
