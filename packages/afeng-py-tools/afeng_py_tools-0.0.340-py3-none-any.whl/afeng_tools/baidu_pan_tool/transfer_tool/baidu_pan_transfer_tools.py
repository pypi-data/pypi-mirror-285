import os
from typing import Callable

from aligo import Aligo, BaseShareFile, BaseFile

from afeng_tools.aliyun_pan_tool import aliyun_pan_tools, aliyun_pan_share_tools
from afeng_tools.baidu_pan_tool.core.baidu_pan_models import UploadCreateResult
from afeng_tools.baidu_pan_tool.tools.baidu_pan_file_path_tools import format_pan_path
from afeng_tools.baidu_pan_tool.transfer_tool.core.alipan_transfer_to_baidupan import alipan_file_save
from afeng_tools.encryption_tool import hashlib_tools
from afeng_tools.file_tool import file_tools
from afeng_tools.log_tool import loguru_tools
from afeng_tools.os_tool import os_tools

logger = loguru_tools.get_logger()


def alipan_to_baidupan(baidupan_access_token: str, ali_pan_path: str = '/',
                       alipan_file_filter_func: Callable[[Aligo, str, BaseFile], bool] = lambda a, x, y: True,
                       baidupan_save_path_func: Callable[[str, str], str] = lambda x, y: f'{x}/{y}',
                       baidupan_save_after_handle_func: Callable[[BaseFile, str, UploadCreateResult], None] = None,
                       is_resource_drive: bool = False,
                       is_init_file_md5: bool = True):
    """
    阿里云盘转存到百度网盘
    :param baidupan_access_token:百度网盘access_token
    :param ali_pan_path: 阿里云盘文件路径
     :param alipan_file_filter_func: 阿里云盘文件过滤函数，只有满足条件的文件才会进行转存，参数：(阿里云盘的路径(包含文件名): alipan_path, 阿里云盘的文件: alipan_file)-> True或False
    :param baidupan_save_path_func: 百度网盘路径函数：(阿里云盘的路径(不包含文件名，根路径为/): alipan_path, 阿里云盘的文件名: alipan_file_name)-> 百度网盘的路径
      :param baidupan_save_after_handle_func:  百度网盘保存后的处理函数，参数：(阿里网盘文件, 百度网盘保存路径（包含文件名）,上传保存结果)
      :param is_resource_drive: 是否是资源盘
      :param is_init_file_md5: 是否初始化文件的md5
    :return:
    """
    transfer_list_file = os.path.join(os_tools.get_user_home(),
                                      f'.alipan_transfer_list-{hashlib_tools.calc_md5(ali_pan_path)}')
    exist_file_list = []
    if os.path.exists(transfer_list_file):
        exist_file_list = file_tools.read_file_lines(transfer_list_file)
    # 阿里云盘
    alipan_api = aliyun_pan_tools.get_ali_api()
    if is_resource_drive:
        alipan_api.default_drive_id = alipan_api.v2_user_get().resource_drive_id
    aliyun_pan_tools.list_all_file(alipan_api, ali_pan_path,
                                   callback_func=lambda pan_path, pan_file: alipan_file_save(
                                       baidupan_access_token=baidupan_access_token,
                                       alipan_api=alipan_api,
                                       alipan_path=pan_path,
                                       alipan_file=pan_file,
                                       transfer_list_file=transfer_list_file,
                                       exist_file_list=exist_file_list,
                                       alipan_file_filter_func=alipan_file_filter_func,
                                       baidupan_save_path_func=baidupan_save_path_func,
                                       baidupan_save_after_handle_func=baidupan_save_after_handle_func,
                                       is_init_file_md5=is_init_file_md5))

    if os.path.exists(transfer_list_file):
        # os.remove(transfer_list_file)
        pass


def alipan_share_transfer_to_baidupan(baidupan_access_token: str, alipan_share_msg: str,
                                      alipan_file_filter_func: Callable[[Aligo, str, BaseShareFile], bool] = lambda a,
                                                                                                                    x,
                                                                                                                    y: True,
                                      baidupan_save_path_func: Callable[[str, str], str] = lambda x, y: f'{x}/{y}',
                                      baidupan_save_after_handle_func: Callable[
                                          [BaseFile, str, UploadCreateResult], None] = None,
                                      is_init_file_md5: bool = True):
    return alipan_share_to_baidupan(baidupan_access_token=baidupan_access_token,
                                    alipan_share_msg=alipan_share_msg,
                                    alipan_file_filter_func=alipan_file_filter_func,
                                    baidupan_save_path_func=baidupan_save_path_func,
                                    baidupan_save_after_handle_func=baidupan_save_after_handle_func,
                                    is_init_file_md5=is_init_file_md5)


def alipan_share_to_baidupan(baidupan_access_token: str, alipan_share_msg: str,
                             alipan_file_filter_func: Callable[[Aligo, str, BaseShareFile], bool] = lambda a, x,
                                                                                                           y: True,
                             baidupan_save_path_func: Callable[[str, str], str] = lambda x, y: f'{x}/{y}',
                             baidupan_save_after_handle_func: Callable[
                                 [BaseFile, str, UploadCreateResult], None] = None,
                             is_init_file_md5: bool = True):
    """
    阿里云盘的分享转存道百度网盘
    :param baidupan_access_token:百度网盘access_token
    :param alipan_share_msg: 阿里云盘分享信息
     :param alipan_file_filter_func: 阿里云盘文件过滤函数，只有满足条件的文件才会进行转存，参数：(阿里云盘的路径(包含文件名): alipan_path, 阿里云盘的文件: alipan_file)-> True或False
    :param baidupan_save_path_func: 百度网盘路径函数：(阿里云盘的路径(不包含文件名，根路径为/): alipan_path, 阿里云盘的文件名: alipan_file_name)-> 百度网盘的路径
      :param baidupan_save_after_handle_func:  百度网盘保存后的处理函数，参数：(百度网盘保存路径（包含文件名）,上传保存结果)
      :param is_init_file_md5: 是否初始化文件的md5
    :return:
    """
    logger.info(alipan_share_msg)
    # 获取阿里云盘中要上传的文件
    alipan_api = aliyun_pan_tools.get_ali_api()
    share_info_result = aliyun_pan_share_tools.get_share_info_by_link(alipan_api, share_msg=alipan_share_msg)

    transfer_list_file = os.path.join(os_tools.get_user_home(),
                                      f'.alipan_transfer_list-{share_info_result.share_id}')
    exist_file_list = []
    if os.path.exists(transfer_list_file):
        exist_file_list = file_tools.read_file_lines(transfer_list_file)
    alipan_share_token = aliyun_pan_share_tools.get_share_token(alipan_api, share_info_result.share_id,
                                                                share_info_result.share_pwd)
    aliyun_pan_share_tools.list_share_all_file(alipan_api, alipan_share_token,
                                               callback_func=lambda _, pan_path, pan_file: alipan_file_save(
                                                   baidupan_access_token=baidupan_access_token,
                                                   alipan_api=alipan_api,
                                                   alipan_path=pan_path,
                                                   alipan_file=pan_file,
                                                   transfer_list_file=transfer_list_file,
                                                   exist_file_list=exist_file_list,
                                                   alipan_file_filter_func=alipan_file_filter_func,
                                                   baidupan_save_path_func=baidupan_save_path_func,
                                                   baidupan_save_after_handle_func=baidupan_save_after_handle_func,
                                                   is_init_file_md5=is_init_file_md5))

    if os.path.exists(transfer_list_file):
        # os.remove(transfer_list_file)
        pass


if __name__ == '__main__':
    alipan_share_transfer_to_baidupan(baidupan_access_token='',
                                      alipan_share_msg='https://www.alipan.com/s/oqCriKvJDig',
                                      alipan_file_filter_func=lambda a, x, y: True,
                                      baidupan_save_path_func=lambda x,
                                                                     y: f'/apps/阿里云转存{format_pan_path(x)}/{format_pan_path(y)}')
