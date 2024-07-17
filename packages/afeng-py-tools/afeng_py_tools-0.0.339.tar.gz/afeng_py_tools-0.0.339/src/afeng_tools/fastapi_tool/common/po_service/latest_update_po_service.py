from afeng_tools.fastapi_tool.common.po_service.base_po_service import PoService


class LatestUpdatePoService(PoService):
    _table_name_ = "tb_latest_update_info"
    pass
