"""
百度网盘文件路径工具
"""
import json
import os
import re
import time
from typing import List

import requests

from afeng_tools.encryption_tool import hashlib_tools
from afeng_tools.file_tool import tmp_file_tools
from afeng_tools.serialization_tool import pickle_tools

import openapi_client
from afeng_tools.baidu_pan_tool.core.baidu_pan_enums import ApiErrorEnum
from openapi_client.api.fileinfo_api import FileinfoApi
from openapi_client.api.multimediafile_api import MultimediafileApi
from afeng_tools.baidu_pan_tool.core.baidu_pan_decorator_tools import auto_fileinfo_api, auto_media_file_api
from afeng_tools.baidu_pan_tool.core.baidu_pan_models import FileInfo, DocFileInfo, ImageInfo, SearchFileInfo, \
    SearchResultInfo, \
    MultimediaFileInfo, VideoInfo, BtInfo, CategoryListResult, CategoryListItem
from afeng_tools.http_tool import http_params_tools
from afeng_tools.log_tool.loguru_tools import get_logger, log_error

logger = get_logger()


def format_pan_path(pan_path: str):
    """格式化网盘路径：去除不能创建文件夹的符号"""
    result = re.sub(r'[^/\w\\-－·（）()【】《》，、。？+ ……·：\\[\\]\\. ]', '', pan_path).strip()
    if '/' in result:
        return '/'.join([tmp.strip().replace('|', '').strip() for tmp in result.split('/')])
    else:
        return result.strip()


def parse_pan_path(pan_path: str):
    """url解码网盘路径"""
    pan_path = pan_path.strip()
    if pan_path.startswith('%2F'):
        return http_params_tools.url_decode(pan_path)
    return pan_path


def list_all_file_with_cache(access_token: str, dir_path: str, recursion: int = 0,
                             order: str = 'name', desc: int = 0, web: int = 0, only_file: bool = False,
                             interval_seconds: float = 10,
                             cache_path: str = tmp_file_tools.get_user_tmp_dir()) -> List[FileInfo]:
    """
    递归获取文件列表: 本接口可以递归获取指定目录下的所有文件列表（包括目录）。

    :param access_token: Access Token
    :param dir_path: 目录名称绝对路径，必须/开头；
    :param recursion: 是否递归，0为否，1为是，默认为0, 当目录下存在文件夹，并想获取到文件夹下的子文件时，可以设置 recursion 参数为1, 即可获取到更深目录层级的文件。
    :param order: 排序字段
                    time(修改时间)
                    name(文件名，注意，此处排序是按字符串排序的)
                    size(大小，目录无大小)，默认为文件类型
    :param desc: 0为升序，1为降序，默认为0
    :param web: 默认为0， 为1时返回缩略图地址
    :param only_file: 是否只有文件
    :param interval_seconds: 间隔秒数，递归查询太过频繁请求接口会报错，这里是两次请求的间隔秒数
    :param cache_path: 缓存路径
    :return: List[FileInfo]
    """
    tmp_file_list = []
    _result = list_all_by_page(access_token, dir_path=dir_path, recursion=recursion, order=order, desc=desc,
                               web=web)
    sleep_value = 0
    while _result is not None and _result == ApiErrorEnum.hit_frequency_limit:
        print(f'[百度网盘路径{dir_path}加载]高频请求，睡眠{interval_seconds + sleep_value}秒')
        time.sleep(interval_seconds + sleep_value)
        _result = list_all_by_page(access_token, dir_path=dir_path, recursion=recursion, order=order, desc=desc,
                                   web=web)
        sleep_value = sleep_value + 5
    if _result and hasattr(_result, 'file_list') and _result.file_list:
        tmp_file_list.extend(_result.file_list)
        page_num = 1
        while _result and (_result.errno == 0 or _result.errno is None) and _result.has_more:
            page_num = page_num + 1
            print(f'[百度网盘路径{dir_path}分页加载]加载第{page_num}页')
            cache_pickle_file = os.path.join(cache_path, 'bd_cache',
                                             hashlib_tools.calc_unique_id([dir_path, page_num]))
            os.makedirs(os.path.dirname(cache_pickle_file), exist_ok=True)
            if os.path.exists(cache_pickle_file):
                tmp_result = pickle_tools.parse_to_obj(cache_pickle_file)[0]
            else:
                time.sleep(interval_seconds)
                tmp_result = list_all_by_page(access_token, dir_path=dir_path, recursion=recursion, order=order,
                                              desc=desc,
                                              start=_result.cursor, web=web)
            sleep_value = 0
            while tmp_result is not None and tmp_result == ApiErrorEnum.hit_frequency_limit:
                print(
                    f'[百度网盘路径{dir_path}分页加载]加载第{page_num}页, 出现高频请求，睡眠{interval_seconds + sleep_value}秒')
                time.sleep(interval_seconds + sleep_value)
                tmp_result = list_all_by_page(access_token, dir_path=dir_path, recursion=recursion, order=order,
                                              desc=desc,
                                              start=_result.cursor, web=web)
                sleep_value = sleep_value + 5
            pickle_tools.save_to_file([tmp_result], cache_pickle_file)
            _result = tmp_result
            if _result and hasattr(_result, 'file_list') and _result.file_list:
                tmp_file_list.extend(_result.file_list)
        if only_file:
            tmp_file_list = list(filter(lambda x: x.isdir == 0, tmp_file_list))
    return tmp_file_list


def list_all_file(access_token: str, dir_path: str, recursion: int = 0,
                  order: str = 'name', desc: int = 0, web: int = 0, only_file: bool = False,
                  interval_seconds: float = 10) -> List[FileInfo]:
    """
    递归获取文件列表: 本接口可以递归获取指定目录下的所有文件列表（包括目录）。
    :param access_token: Access Token
    :param dir_path: 目录名称绝对路径，必须/开头；
    :param recursion: 是否递归，0为否，1为是，默认为0, 当目录下存在文件夹，并想获取到文件夹下的子文件时，可以设置 recursion 参数为1, 即可获取到更深目录层级的文件。
    :param order: 排序字段
                    time(修改时间)
                    name(文件名，注意，此处排序是按字符串排序的)
                    size(大小，目录无大小)，默认为文件类型
    :param desc: 0为升序，1为降序，默认为0
    :param web: 默认为0， 为1时返回缩略图地址
    :param only_file: 是否只有文件
    :param interval_seconds: 间隔秒数，递归查询太过频繁请求接口会报错，这里是两次请求的间隔秒数
    :return: List[FileInfo]
    """
    tmp_file_list = []
    _result = list_all_by_page(access_token, dir_path=dir_path, recursion=recursion, order=order, desc=desc,
                               web=web)
    sleep_value = 0
    while _result is not None and _result == ApiErrorEnum.hit_frequency_limit:
        print(f'[百度网盘路径{dir_path}加载]高频请求，睡眠{interval_seconds + sleep_value}秒')
        time.sleep(interval_seconds + sleep_value)
        _result = list_all_by_page(access_token, dir_path=dir_path, recursion=recursion, order=order, desc=desc,
                                   web=web)
        sleep_value = sleep_value + 5
    if _result and hasattr(_result, 'file_list') and _result.file_list:
        tmp_file_list.extend(_result.file_list)
        page_num = 1
        while _result and (_result.errno == 0 or _result.errno is None) and hasattr(_result,
                                                                                    'has_more') and _result.has_more:
            page_num = page_num + 1
            print(f'[百度网盘路径{dir_path}分页加载]加载第{page_num}页')
            time.sleep(interval_seconds)
            tmp_result = list_all_by_page(access_token, dir_path=dir_path, recursion=recursion, order=order, desc=desc,
                                          start=_result.cursor, web=web)
            sleep_value = 0
            while tmp_result is not None and tmp_result == ApiErrorEnum.hit_frequency_limit:
                print(
                    f'[百度网盘路径{dir_path}分页加载]加载第{page_num}页, 出现高频请求，睡眠{interval_seconds + sleep_value}秒')
                time.sleep(interval_seconds + sleep_value)
                tmp_result = list_all_by_page(access_token, dir_path=dir_path, recursion=recursion, order=order,
                                              desc=desc,
                                              start=_result.cursor, web=web)
                sleep_value = sleep_value + 5
            _result = tmp_result
            if _result and hasattr(_result, 'file_list') and _result.file_list:
                tmp_file_list.extend(_result.file_list)
        if only_file:
            tmp_file_list = list(filter(lambda x: x.isdir == 0, tmp_file_list))
    return tmp_file_list


@auto_media_file_api
def list_all_by_page(access_token: str, dir_path: str, recursion: int = 0,
                     order: str = 'name', desc: int = 0, start: int = 0, limit: int = 1000,
                     web: int = 0,
                     api_instance: MultimediafileApi = None) -> MultimediaFileInfo | ApiErrorEnum:
    """
    获取文件列表（前1000条）: 本接口可以递归获取指定目录下的文件列表。
    :param access_token: Access Token
    :param dir_path: 目录名称绝对路径，必须/开头；
    :param recursion: 是否递归，0为否，1为是，默认为0, 当目录下存在文件夹，并想获取到文件夹下的子文件时，可以设置 recursion 参数为1, 即可获取到更深目录层级的文件。
    :param order: 排序字段
                    time(修改时间)
                    name(文件名，注意，此处排序是按字符串排序的)
                    size(大小，目录无大小)，默认为文件类型
    :param desc: 0为升序，1为降序，默认为0
    :param start: 查询起点，默认为0，当返回has_more=1时，应使用返回的cursor作为下一次查询的起点
    :param limit: 查询数目，默认为1000； 如果设置start和limit参数，则建议最大设置为1000
    :param web: 默认为0， 为1时返回缩略图地址
    :param api_instance: 自动注入MultimediafileApi
    :return: MultimediaFileInfo | ApiErrorEnum
    """
    try:
        api_response = api_instance.xpanfilelistall(access_token, dir_path, recursion,
                                                    order=order, desc=desc, start=start, limit=limit,
                                                    web=str(web))
        if api_response.get('errno') == 0:

            multi_info = MultimediaFileInfo(
                has_more=api_response['has_more'] == 1,
                cursor=api_response['cursor']
            )
            multi_info.file_list = [FileInfo(**tmp_data) for tmp_data in api_response['list']]
            return multi_info
        elif api_response.get('errno') == 42213:
            log_error(logger, f"[BaiduPan]文件或目录[{dir_path}]无权访问搜索")
            return ApiErrorEnum.no_permission_to_access
        elif api_response.get('errno') == 31066:
            log_error(logger, f"[BaiduPan]文件或目录[{dir_path}]不存在，无法进行搜索")
            return ApiErrorEnum.file_does_not_exist
        elif api_response.get('errno') == 31034:
            log_error(logger, f"[BaiduPan]{dir_path}命中频控,listall接口的请求频率建议不超过每分钟8-10次")
            return ApiErrorEnum.hit_frequency_limit
        else:
            log_error(logger, f"[BaiduPan]搜索目录[{dir_path}]下文件列表失败，api_response: {api_response}")
    except openapi_client.ApiException as e:
        try:
            api_response = json.loads(e.body)
            if api_response.get('errno') == 42213:
                log_error(logger, f"[BaiduPan]文件或目录[{dir_path}]无权访问搜索")
                return ApiErrorEnum.no_permission_to_access
            elif api_response.get('errno') == 31066:
                log_error(logger, f"[BaiduPan]文件或目录[{dir_path}]不存在，无法进行搜索")
                return ApiErrorEnum.file_does_not_exist
            elif api_response.get('errno') == 31034:
                log_error(logger, f"[BaiduPan]{dir_path}命中频控,listall接口的请求频率建议不超过每分钟8-10次")
                return ApiErrorEnum.hit_frequency_limit
        except Exception:
            pass
        log_error(logger, "[BaiduPan]Exception when calling MultimediafileApi->xpanfilelistall", e)


@auto_fileinfo_api
def list_file_by_page(access_token: str, dir_path: str = '/', order: str = 'name', desc: int = 0,
                      start: int = 0, limit: int = 1000, web: int = 0, folder: int = 0, show_empty: int = 1,
                      api_instance: FileinfoApi = None) -> list[FileInfo]:
    """
    获取文件列表（前1000条）: 本接口用于获取用户网盘中指定目录下的文件列表。返回的文件列表支持排序、分页等操作。
    :param access_token: Access Token
    :param dir_path: 需要list的目录，以/开头的绝对路径, 默认为/
    :param order: 排序字段：默认为name；
                time表示先按文件类型排序，后按修改时间排序；
                name表示先按文件类型排序，后按文件名称排序；(注意，此处排序是按字符串排序的)
                size表示先按文件类型排序，后按文件大小排序。
    :param desc: 默认为升序，设置为1实现降序, 排序的对象是当前目录下所有文件，不是当前分页下的文件
    :param start: 起始位置，从0开始
    :param limit: 查询数目，默认为1000，建议最大不超过1000
    :param web: 值为1时，返回dir_empty属性和缩略图数据
    :param folder: 是否只返回文件夹，0 返回所有，1 只返回文件夹，且属性只返回path字段
    :param show_empty: 是否返回dir_empty属性，0 不返回，1 返回
    :param api_instance: 自动注入的 FileinfoApi
    :return:
    """
    try:
        api_response = api_instance.xpanfilelist(access_token, dir=dir_path,
                                                 start=str(start), limit=limit,
                                                 order=order, desc=desc, web=str(web),
                                                 folder=str(folder), showempty=show_empty)
        if api_response['errno'] == 0:
            return [FileInfo(**tmp_data) for tmp_data in api_response['list']]
        elif api_response['errno'] == -7:
            log_error(logger, f"文件或目录[{dir_path}]无权访问，响应信息：{api_response}")
        elif api_response['errno'] == -9:
            log_error(logger, f"文件或目录[{dir_path}]不存在，响应信息：{api_response}")
        else:
            log_error(logger, f"获取目录[{dir_path}]下文件列表失败，响应信息：{api_response}")
    except openapi_client.ApiException as e:
        log_error(logger, "[BaiduPan]Exception when calling FileinfoApi->xpanfilelist", e)


@auto_fileinfo_api
def list_image(access_token: str, dir_path: str = '/',
               page_num: int = 1, page_size: int = 1000,
               order: str = 'name', desc: int = 1,
               recursion: int = 0, web: int = 0,
               api_instance: FileinfoApi = None) -> List[ImageInfo]:
    """
     获取图片列表（前1000条）: 获取用户指定目录下的图片列表
     :param access_token: Access Token
     :param dir_path: 目录名称，以/开头的绝对路径, 默认为/ , 路径包含中文时需要UrlEncode编码
     :param page_num: 页码，从1开始， 如果不指定页码，则为不分页模式，返回所有的结果。如果指定page参数，则按修改时间倒序排列
     :param page_size: 一页返回的文档数， 默认值为1000，建议最大值不超过1000
     :param order:  排序字段：默认为name
                        time按修改时间排序，
                        name按文件名称排序，
                        size按文件大小排序，
     :param desc: 0为升序，1为降序，默认为1
     :param recursion:  是否需要递归，0为不需要，1为需要，默认为0, 递归是指：当目录下有文件夹，使用此参数，可以获取到文件夹下面的文档
     :param web: 为1时返回文档预览地址lodocpreview
     :param api_instance: 自动注入的 FileinfoApi
     :return: List[ImageInfo]
     """
    try:
        api_response = api_instance.xpanfileimagelist(access_token, parent_path=dir_path,
                                                      recursion=str(recursion),
                                                      page=page_num, num=page_size,
                                                      order=order, desc=str(desc), web=str(web))
        if api_response['errno'] == 0:
            return [ImageInfo(**tmp_data) for tmp_data in api_response['info']]
        else:
            log_error(logger, f"[BaiduPan]获取目录[{dir_path}]下图片列表失败:{api_response}")
    except openapi_client.ApiException as e:
        log_error(logger, f"[BaiduPan][{dir_path}]Exception when calling FileinfoApi->xpanfileimagelist", e)


@auto_fileinfo_api
def list_doc(access_token: str, dir_path: str = '/',
             page_num: int = 1, page_size: int = 1000,
             order: str = 'name', desc: int = 1,
             recursion: int = 0, web: int = 0,
             api_instance: FileinfoApi = None) -> List[DocFileInfo]:
    """
    获取文档列表（前1000条）：获取用户指定目录下的文档列表。
    :param access_token: Access Token
    :param dir_path: 目录名称，以/开头的绝对路径, 默认为/
    :param page_num: 页码，从1开始， 如果不指定页码，则为不分页模式，返回所有的结果。如果指定page参数，则按修改时间倒序排列
    :param page_size: 一页返回的文档数， 默认值为1000，建议最大值不超过1000
    :param order:  排序字段： 默认为name
                        time按修改时间排序
                        name按文件名称排序
                        size按文件大小排序
    :param desc: 0为升序，1为降序，默认为1
    :param recursion:  是否需要递归，0为不需要，1为需要，默认为0, 递归是指：当目录下有文件夹，使用此参数，可以获取到文件夹下面的文档
    :param web: 为1时返回文档预览地址lodocpreview
    :param api_instance: 自动注入的 FileinfoApi
    :return: List[DocFileInfo]
    """
    try:
        api_response = api_instance.xpanfiledoclist(access_token, parent_path=dir_path, order=order, desc=str(desc),
                                                    recursion=str(recursion), page=page_num, num=page_size,
                                                    web=str(web))
        if api_response['errno'] == 0:
            return [DocFileInfo(**tmp_data) for tmp_data in api_response['info']]
        else:
            log_error(logger, f"[BaiduPan][{dir_path}]下文档列表失败: {api_response}")
    except openapi_client.ApiException as e:
        log_error(logger, f"[BaiduPan][{dir_path}]Exception when calling FileinfoApi->xpanfiledoclist", e)


def list_video(access_token: str, dir_path: str = '/',
               page_num: int = 1, page_size: int = 1000,
               order: str = 'name', desc: int = 1,
               recursion: int = 0, web: int = 0) -> list[VideoInfo]:
    """
    获取视频列表: 本接口用于获取用户指定目录下的视频列表.
    :param access_token: Access Token
    :param dir_path: 目录名称，以/开头的绝对路径, 默认为/
    :param page_num: 页码，从1开始， 如果不指定页码，则为不分页模式，返回所有的结果。如果指定page参数，则按修改时间倒序排列
    :param page_size: 一页返回的文件数， 默认值为1000, 最大值建议不超过1000
    :param order: 排序字段， 默认为name
                    time按修改时间排序
                    name按文件名称排序(注意，此处排序是按字符串排序的）
                    size按文件大小排序
    :param desc: 0为升序，1为降序，默认为1
    :param recursion: 是否需要递归，0为不需要，1为需要，默认为0
                        递归是指：当目录下有文件夹，使用此参数，可以获取到文件夹下面的视频
    :param web: 为1时返回视频预览缩略图
    :return: list[VideoInfo]
    """
    params = {
        'method': 'videolist',
        'access_token': access_token,
        'parent_path': http_params_tools.url_encode(dir_path),
        'page': page_num,
        'num': page_size,
        'order': order,
        'desc': desc,
        'recursion': recursion,
        'web': web
    }
    headers = {
        'User-Agent': 'pan.baidu.com'
    }
    try:
        response = requests.get('http://pan.baidu.com/rest/2.0/xpan/file', params=params, headers=headers)
        response.encoding = 'utf8'
        api_response = response.json()
        if api_response['errno'] == 0:
            return [VideoInfo(**tmp_data) for tmp_data in api_response['info']]
        else:
            log_error(logger, f"[BaiduPan][{dir_path}]下视频列表失败: {api_response}")
    except openapi_client.ApiException as e:
        log_error(logger, f"[BaiduPan][{dir_path}]Exception when calling FileinfoApi->xpanfilevideolist", e)


def list_bt(access_token: str, dir_path: str = '/',
            page_num: int = 1, page_size: int = 1000,
            order: str = 'name', desc: int = 1,
            recursion: int = 0) -> list[BtInfo]:
    """
    获取bt列表: 本接口用于获取用户指定路径下的bt文件列表。
    :param access_token: Access Token
    :param dir_path: 目录名称，以/开头的绝对路径, 默认为/
    :param page_num: 页码，从1开始， 如果不指定页码，则为不分页模式，返回所有的结果。如果指定page参数，则按修改时间倒序排列
    :param page_size: 一页返回的文件数， 默认值为1000, 最大值建议不超过1000
    :param order: 排序字段， 默认为name
                    time按修改时间排序
                    name按文件名称排序(注意，此处排序是按字符串排序的）
                    size按文件大小排序
    :param desc: 0为升序，1为降序，默认为1
    :param recursion: 是否需要递归，0为不需要，1为需要，默认为0
                        递归是指：当目录下有文件夹，使用此参数，可以获取到文件夹下面的bt文件
    :return: list[BtInfo]
    """
    params = {
        'method': 'btlist',
        'access_token': access_token,
        'parent_path': http_params_tools.url_encode(dir_path),
        'page': page_num,
        'num': page_size,
        'order': order,
        'desc': desc,
        'recursion': recursion,
    }
    headers = {
        'User-Agent': 'pan.baidu.com',
        'Cookie': 'PANWEB=1; BAIDUID=AC26BE01592777C2F2253ECBC0E5780B:FG=1'
    }
    try:
        response = requests.get('http://pan.baidu.com/rest/2.0/xpan/file', params=params, headers=headers)
        response.encoding = 'utf8'
        api_response = response.json()
        if api_response['errno'] == 0:
            return [BtInfo(**tmp_data) for tmp_data in api_response['info']]
        else:
            log_error(logger, f"[BaiduPan][{dir_path}]下bt列表失败: {api_response}")
    except openapi_client.ApiException as e:
        log_error(logger, f"[BaiduPan][{dir_path}]Exception when calling FileinfoApi->xpanfilebtlist", e)


@auto_fileinfo_api
def search(access_token: str, key_word: str, dir_path: str = '/',
           page_num: int = 1, page_size: int = 500,
           recursion: bool = False, web: bool = False,
           api_instance: FileinfoApi = None) -> SearchResultInfo:
    """
    搜索文件: 本接口用于获取用户指定目录下，包含指定关键字的文件列表。
    :param access_token: Access T
    :param key_word: 搜索关键字，最大30字符（UTF8格式）
    :param dir_path: 搜索目录，默认根目录
    :param page_num: 页数，从1开始，缺省则返回所有条目
    :param page_size: 默认为500，不能修改
    :param recursion: 是否递归，带这个参数就会递归，否则不递归
    :param web: 是否展示缩略图信息，带这个参数会返回缩略图信息，否则不展示缩略图信息
    :param api_instance: 自动注入的 FileinfoApi
    :return: SearchResultInfo
    """
    try:
        param_dict = {'key': key_word, 'dir': dir_path, 'page': str(page_num), 'num': str(page_size)}
        if web:
            param_dict['web'] = str(1)
        if recursion:
            param_dict['recursion'] = str(1)
        api_response = api_instance.xpanfilesearch(access_token, **param_dict)
        if api_response['errno'] == 0:
            result = SearchResultInfo(has_more=api_response['has_more'] == 1,
                                      content_list=api_response['contentlist'])
            result.file_list = [SearchFileInfo(**tmp_data) for tmp_data in api_response['list']]
            return result
        elif api_response['errno'] == -7:
            log_error(logger, f"[BaiduPan]目录[{dir_path}]无权访问搜索")
        elif api_response['errno'] == -9:
            log_error(logger, f"[BaiduPan]目录[{dir_path}]不存在，无法进行搜索")
        else:
            log_error(logger, f"[BaiduPan]搜索目录[{dir_path}]下文件[{key_word}]失败: {api_response}")
    except openapi_client.ApiException as e:
        log_error(logger, f"[BaiduPan][{dir_path}]Exception when calling FileinfoApi->xpanfilesearch", e)


def list_category_file(access_token: str, category: int, dir_path: str = '/',
                       show_dir: int = 0, recursion: int = 0, ext: str = None,
                       start: int = 0, limit: int = 1000,
                       order: str = 'name', desc: int = 1, device_id: str = None) -> CategoryListResult:
    """
    获取分类文件列表: 本接口用于获取用户目录下指定类型的文件列表。
    :param access_token: Access Token
    :param category: 文件类型，1 视频、2 音频、3 图片、4 文档、5 应用、6 其他、7 种子, 多个category使用英文逗号分隔，示例：3,4
    :param dir_path: 目录名称，以/开头的绝对路径, 默认为/
    :param show_dir: 是否展示文件夹，0:否(默认) 1:是
    :param recursion: 是否需要递归，0为不需要，1为需要，默认为0 （注意recursion=1时不支持show_dir=1）
    :param ext: 需要的文件格式，多个格式以英文逗号分隔，示例: txt,epub，默认为category下所有格式
    :param start: 查询起点，默认为0
    :param limit: 查询数目，最大1000，默认1000
    :param order: 排序字段， 默认为name
                    time按修改时间排序
                    name按文件名称排序(注意，此处排序是按字符串排序的）
                    size按文件大小排序
    :param desc: 0为升序，1为降序，默认为1
    :param device_id: 设备ID，硬件设备必传
    :return: CategoryListResult
    """
    params = {
        'method': 'categorylist',
        'access_token': access_token,
        'category': category,
        'show_dir': show_dir,
        'parent_path': http_params_tools.url_encode(dir_path),
        'recursion': recursion,
        'ext': ext,
        'start': start,
        'limit': limit,
        'order': order,
        'desc': desc,
        'device_id': device_id
    }
    headers = {
        'User-Agent': 'pan.baidu.com'
    }
    try:
        response = requests.get('http://pan.baidu.com/rest/2.0/xpan/multimedia', params=params, headers=headers)
        response.encoding = 'utf8'
        api_response = response.json()
        if api_response['errno'] == 0:
            result = CategoryListResult(has_more=api_response['has_more'] == 1,
                                        cursor=api_response['cursor'])
            result.file_list = [CategoryListItem(**tmp_data) for tmp_data in api_response['list']]
            return result
        else:
            log_error(logger, f"[BaiduPan]获取[{dir_path}]下分类[{category}]文件列表失败: {api_response}")
    except openapi_client.ApiException as e:
        log_error(logger, f"[BaiduPan][{dir_path}]Exception when calling multimedia->categorylist", e)
