from typing import Any
from sqlalchemy.orm import Session

from afeng_tools.fastapi_tool.common.po_service.base_po_service import PoService
from afeng_tools.pydantic_tool.model.common_models import LinkItem
from afeng_tools.sqlalchemy_tools.decorator.sqlalchemy_session_decorator import auto_db


class TagPoService(PoService):
    """
    使用示例：tag_po_service = TagPoService(app_info.db_code, TagInfoPo)
    """
    _table_name_ = "tb_tag_info"

    def get_by_code(self, type_code: str, code: str) -> Any:
        return self.get(self.model_type.type_code == type_code, self.model_type.code == code)

    @classmethod
    def convert_to_link_item(cls, tag_po, is_active: bool = False, tag_href_prefix: str = '/tag') -> LinkItem:
        return LinkItem(
            target='_blank',
            title=tag_po.title,
            href=f'{tag_href_prefix}/{tag_po.code}',
            code=tag_po.code,
            description=tag_po.description,
            is_active=is_active)

    def query_tag_by_relation_type_code(self, type_code: str, type_value: str, tag_relation_info_po_class) -> list:
        """
        通过 type_code和type_value查询关联的标签
        :param type_code:
        :param type_value:
        :param tag_relation_info_po_class:TagRelationInfoPo类
        :return:
        """
        @auto_db(db_code=self.db_code)
        def _query_by_type_code(_type_code: str, _type_value: str, _tag_relation_info_po_class, db: Session = None) -> list:
            db_query = (db.query(self.model_type, _tag_relation_info_po_class)
                        .select_from(self.model_type).join(_tag_relation_info_po_class,
                                                           _tag_relation_info_po_class.tag_code == self.model_type.code,
                                                           isouter=True))
            db_query = (
                db_query.filter(_tag_relation_info_po_class.type_code == _type_code,
                                _tag_relation_info_po_class.type_value == _type_value)
                .order_by(_tag_relation_info_po_class.order_num.desc()))
            query_result = db_query.all()
            if query_result:
                return [type_info_po for type_info_po, tag_relation_po in query_result if type_info_po]
            return []

        return _query_by_type_code(_type_code=type_code, _type_value=type_value,
                                   _tag_relation_info_po_class=tag_relation_info_po_class)


class TagRelationPoService(PoService):
    """
    使用示例：tag_relation_po_service = TagRelationPoService(app_info.db_code, TagRelationInfoPo)
    """
    _table_name_ = "tb_tag_relation_info"

    def query_by_type_code(self, type_code: str) -> list[Any]:
        return self.get(self.model_type.type_code == type_code)

    def get_by_tag_code(self, type_code: str, tag_code: str) -> Any:
        return self.get(self.model_type.type_code == type_code, self.model_type.tag_code == tag_code)
