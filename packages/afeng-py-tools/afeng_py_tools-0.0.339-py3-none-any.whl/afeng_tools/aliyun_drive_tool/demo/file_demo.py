import datetime

import requests

from .. import aliyun_drive_auth_tools, aliyun_drive_share_tools, aliyun_drive_file_tools, \
    aliyun_drive_download_tools


def run():
    alipan_api = aliyun_drive_auth_tools.get_alipan_api(use_resource_drive=True)
    # child_list = aliyun_drive_file_tools.get_file_list(alipan_api, parent_file_id='66438c41fe482caa3a70492b86884b7e87532310')
    file_info = aliyun_drive_file_tools.get_file_by_path(alipan_api,
                                                         file_path='23红宝书时间规划表.pdf',
                                                         parent_file_id='664792aeefb2acd9e80b42ac9ad762339f0e2bbf')

    # download_url_resp = alipan_api.get_download_url(file_id=file_info.file_id)
    url = aliyun_drive_download_tools.get_download_url(alipan_api, file_id=file_info.file_id)
    resp = requests.get(url, headers={
        'Referer': 'https://www.aliyundrive.com/',
        'Origin': 'https://www.aliyundrive.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    })
    print()


if __name__ == '__main__':
    run()
    result = datetime.datetime.fromtimestamp(1717443579)
    print()
