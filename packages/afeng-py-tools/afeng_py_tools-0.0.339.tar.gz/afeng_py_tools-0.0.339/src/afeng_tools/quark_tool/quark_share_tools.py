"""
夸克分享工具
"""
import json
import time

import urllib.parse

from afeng_tools.quark_tool.core import quark_http_tools
from afeng_tools.quark_tool.core.quark_items import ShareToken, ShareData, PageMetadata
from afeng_tools.quark_tool.core.quark_response_items import ShareTokenResponse, ShareDataResponse


def get_share_token(pwd_id: str, pwd: str = '') -> ShareToken:
    resp_json = quark_http_tools.post(
        url=f'https://drive-pc.quark.cn/1/clouddrive/share/sharepage/token?pr=ucpro&fr=pc&uc_param_str=&__dt=1653&__t={int(time.time())}138',
        json_params={
            'pwd_id': pwd_id,
            'passcode': pwd
        })
    if resp_json:
        response = ShareTokenResponse(**resp_json)
        if response.status == 200:
            share_token = response.data
            share_token.pwd_id = pwd_id
            return share_token


def get_share_info(share_token: ShareToken, pdir_fid: str = '0', page_num: int = 1, page_size: int = 50) -> tuple[
    PageMetadata, ShareData]:
    resp_json = quark_http_tools.get(
        url=f'https://drive-pc.quark.cn/1/clouddrive/share/sharepage/detail?pr=ucpro&fr=pc&uc_param_str='
            f'&pwd_id={share_token.pwd_id}'
            f'&stoken={urllib.parse.quote(share_token.stoken)}'
            f'&pdir_fid={pdir_fid}&force=0'
            f'&_page={page_num}&_size={page_size}&_fetch_banner=1&_fetch_share=1&_fetch_total=1'
            f'&_sort=file_type:asc,updated_at:desc&__dt=2129&__t={int(time.time())}374')
    if resp_json:
        response = ShareDataResponse(**resp_json)
        if response.status == 200:
            return response.metadata, response.data


if __name__ == '__main__':
    # tmp_share_token = get_share_token(pwd_id='de8e831c4e4f')
    # print(json.dumps(tmp_share_token.model_dump(mode='json'), ensure_ascii=False, indent=4))
    # print(int(time.time()))
    tmp_share_token = ShareToken(pwd_id='de8e831c4e4f', stoken="AmDTDLfPcWmN+xqB+vWvfVB82vJ8uwZz48c8V6WTdLs=")
    page_data, share_data = get_share_info(tmp_share_token)
    print()
    pass
