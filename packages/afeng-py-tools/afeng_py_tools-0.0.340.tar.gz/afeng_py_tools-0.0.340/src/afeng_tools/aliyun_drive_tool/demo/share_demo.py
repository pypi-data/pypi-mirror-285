from .. import aliyun_drive_auth_tools, aliyun_drive_share_tools


def run():
    alipan_api = aliyun_drive_auth_tools.get_alipan_api()
    share_token = aliyun_drive_share_tools.get_share_token(alipan_api, share_id='Y31kDxNjphx')
    share_file_list = aliyun_drive_share_tools.get_share_file_list(alipan_api, share_token=share_token,
                                                                   parent_file_id='64a9326505e0e8e41fb245ae842f726ccc914133')
    for tmp_share_file in share_file_list:
        tmp_share_info = aliyun_drive_share_tools.get_share_link_download_url(alipan_api,
                                                                              file_id=tmp_share_file.file_id,
                                                                              share_token=share_token)
        print()


def run_download_file_demo():
    alipan_api = aliyun_drive_auth_tools.get_alipan_api()
    share_token = aliyun_drive_share_tools.get_share_token(alipan_api, share_id='Y31kDxNjphx')
    share_file_list = aliyun_drive_share_tools.get_share_file_list(alipan_api, share_token=share_token,
                                                                   parent_file_id='64a9326505e0e8e41fb245ae842f726ccc914133')
    for tmp_share_file in share_file_list:
        tmp_file = aliyun_drive_share_tools.download_share_file(alipan_api, share_token=share_token,
                                                                share_file=tmp_share_file,
                                                                local_folder='./output')
        print(tmp_file)


def run_download_folder_demo():
    alipan_api = aliyun_drive_auth_tools.get_alipan_api()
    share_token = aliyun_drive_share_tools.get_share_token(alipan_api, share_id='Y31kDxNjphx')
    share_file = aliyun_drive_share_tools.get_share_file(alipan_api, share_token,
                                                         file_id='64a9326505e0e8e41fb245ae842f726ccc914133')
    result = aliyun_drive_share_tools.download_share_file(alipan_api, share_token=share_token,
                                                          share_file=share_file,
                                                          local_folder='./output')
    print(result)


if __name__ == '__main__':
    # run()
    # run_download_file_demo()
    run_download_folder_demo()
