"""
列表工具
"""
import math
from typing import Any


def divide_to_groups(list_value: list[Any], group_length: int = 1000) -> list[list[Any]]:
    """
    将列表进行分组
    :param list_value: 列表值, 如：[1,2,3,4,5]
    :param group_length: 分组长度
    :return: 分组后的列表， 如：[[1,2],[3,4],[5]]
    """
    result_list = []
    group_count = math.ceil(len(list_value) / group_length)
    for i in range(group_count):
        result_list.append(list_value[i * group_length:(i + 1) * group_length])
    return result_list


def list_to_subgroup(group_by_attr: str, data_list: list) -> dict[Any, list]:
    """
    list列表拆分成子分组列表
    :param group_by_attr:分组字段
    :param data_list:数据列表
    :return: {分组字段值：[分组对应列表]}
    """
    result_dict = dict()
    for tmp_data in data_list:
        tmp_attr_value = getattr(tmp_data, group_by_attr)
        tmp_list = result_dict.get(tmp_attr_value)
        if tmp_list is None:
            result_dict[tmp_attr_value] = [tmp_data]
        else:
            tmp_list.append(tmp_data)
    return result_dict
