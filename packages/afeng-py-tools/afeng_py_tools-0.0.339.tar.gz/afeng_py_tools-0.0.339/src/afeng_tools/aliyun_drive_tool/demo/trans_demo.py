import os
from admin import admin_settings
from afeng_tools.baidu_pan_tool import baidu_pan_tools
from afeng_tools.baidu_pan_tool.tools.baidu_pan_file_path_tools import format_pan_path
from afeng_tools.baidu_pan_tool.transfer_tool.core.alipan_transfer_to_baidupan import alipan_file_save
from afeng_tools.file_tool import file_tools
from afeng_tools.os_tool import os_tools
from aligo import Aligo, BaseFile

from .. import aliyun_drive_auth_tools, aliyun_drive_file_tools, aliyun_drive_download_tools

baidupan_access_token = baidu_pan_tools.get_access_token()

transfer_list_file = os.path.join(os_tools.get_user_home(),
                                  f'.alipan_transfer_list-665dbcbcc3379ac1ab604c99b17d5683e0aceb3c')
exist_file_list = []
if os.path.exists(transfer_list_file):
    exist_file_list = file_tools.read_file_lines(transfer_list_file)


def handle_file(alipan_api: Aligo, pan_file: BaseFile):
    if pan_file.type == 'folder':
        return
    pan_file.download_url = aliyun_drive_download_tools.get_download_url(alipan_api, file_id=pan_file.file_id)
    alipan_file_save(
        baidupan_access_token=baidupan_access_token,
        alipan_api=alipan_api,
        alipan_path=pan_file.path,
        alipan_file=pan_file,
        transfer_list_file=transfer_list_file,
        exist_file_list=exist_file_list,
        alipan_file_filter_func=lambda a, x, y: True,
        baidupan_save_path_func=lambda x, y: f'/apps/阿里云转存/分享转存{format_pan_path(x)}/{format_pan_path(y)}',
        is_init_file_md5=False)


def run():
    alipan_api = aliyun_drive_auth_tools.get_alipan_api(use_resource_drive=True)
    file_id = '665dbcbcc3379ac1ab604c99b17d5683e0aceb3c'
    root_file = aliyun_drive_file_tools.get_file(alipan_api, file_id)
    aliyun_drive_file_tools.iterate_handle_all_file(alipan_api,
                                                    iterate_handle_func=handle_file,
                                                    parent_file_id=file_id, parent_path=f'/{root_file.name}')


if __name__ == '__main__':
    run()
    pass
