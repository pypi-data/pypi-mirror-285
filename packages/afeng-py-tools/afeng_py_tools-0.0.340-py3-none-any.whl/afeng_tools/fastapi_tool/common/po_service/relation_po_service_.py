from afeng_tools.fastapi_tool.common.po_service.base_po_service import PoService


class RelationPoService(PoService):
    """
    使用示例：relation_po_service = RelationPoService(app_info.db_code, RelationInfoPo)
    """
    _table_name_ = "tb_relation_info"
    pass
