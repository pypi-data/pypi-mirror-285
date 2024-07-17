from typing import Any

from afeng_tools.fastapi_tool.common.po_service.base_po_service import PoService
from afeng_tools.fastapi_tool.common.service import icon_base_service
from afeng_tools.pydantic_tool.model.common_models import LinkItem
from afeng_tools.sequence_tool import list_tools


class LinkPoService(PoService):
    """
    使用示例：link_po_service = LinkPoService(app_info.db_code, LinkInfoPo)
    """
    _table_name_ = "tb_link_info"

    def query_by_type_code(self, type_code: str) -> list[Any]:
        return self.query_more(self.model_type.type_code == type_code)

    def get_by_code(self, type_code: str, code: str) -> Any:
        return self.get(self.model_type.type_code == type_code, self.model_type.code == code)

    @classmethod
    def convert_to_link_item(cls, link_po, is_active: bool = False) -> LinkItem:
        return LinkItem(
            title=link_po.title,
            href=link_po.link_url,
            code=link_po.code,
            description=link_po.description,
            image=icon_base_service.get_icon_code(icon_type=link_po.icon_type,
                                                  icon_value=link_po.icon_value,
                                                  alt=link_po.title,
                                                  image_src=link_po.image_src),
            target=link_po.target.value if link_po.target else '_blank',
            is_ok=link_po.is_ok if link_po.is_ok is not None else True,
            is_active=is_active)

    @classmethod
    def convert_po_2_item(cls, data_list: list) -> list[LinkItem]:
        return [LinkItem(
            href=tmp.link_url,
            code=f'{tmp.type_code}__{tmp.code}',
            title=tmp.title,
            description=tmp.description,
            image=icon_base_service.get_icon_code(icon_type=tmp.icon_type,
                                                  icon_value=tmp.icon_value,
                                                  alt=tmp.title,
                                                  image_src=tmp.image_src),
            target=tmp.target.value if tmp.target else '_blank',
            is_ok=tmp.is_ok if tmp.is_ok is not None else True,
        ) for tmp in data_list] if data_list else []

    def query_link_tree(self, type_code: str, parent_code: str = None,
                        parent_code_dict: dict = None) -> list[LinkItem]:
        """查询链接树"""
        if parent_code_dict is None:
            all_link_list = self.query_more(self.model_type.type_code == type_code)
            parent_code_dict = list_tools.list_to_subgroup(group_by_attr='parent_code', data_list=all_link_list)
        result_list = []
        child_po_list = parent_code_dict.get(parent_code)
        if child_po_list:
            for tmp_child_po in child_po_list:
                tmp_link_item = self.convert_to_link_item(tmp_child_po)
                if parent_code_dict.get(tmp_child_po.code):
                    tmp_link_item.children = self.query_link_tree(type_code=type_code,
                                                                  parent_code=tmp_child_po.code,
                                                                  parent_code_dict=parent_code_dict)
                result_list.append(tmp_link_item)
        return result_list
