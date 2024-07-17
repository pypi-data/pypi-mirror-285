from afeng_tools.fastapi_tool.common.po_service.base_po_service import PoService
from afeng_tools.sqlalchemy_tools.core.sqlalchemy_enums import SortTypeEnum


class CountPoService(PoService):
    _table_name_ = "tb_count_info"
    pass

    def save_count(self, type_code: str, type_value: str, count_value: int):
        """保存数量"""
        po = self.model_type(
            type_code=type_code,
            type_value=type_value,
            count_value=count_value
        )
        self.save(po, self.model_type.type_code == po.type_code,
                  self.model_type.type_value == po.type_value)

    def query_count(self, type_code: str, type_value_list: list[str] = None,
                    sort_column: str = 'type_value',
                    sort_type: SortTypeEnum = SortTypeEnum.asc) -> dict[str, int]:
        """查询数量"""
        if type_value_list:
            po_list = self.query_more(self.model_type.type_code == type_code,
                                      self.model_type.type_value.in_(type_value_list),
                                      sort_column=sort_column,
                                      sort_type=sort_type)
        else:
            po_list = self.query_more(self.model_type.type_code == type_code,
                                      sort_column=sort_column,
                                      sort_type=sort_type)
        return {tmp.type_value: tmp.count_value for tmp in po_list}
