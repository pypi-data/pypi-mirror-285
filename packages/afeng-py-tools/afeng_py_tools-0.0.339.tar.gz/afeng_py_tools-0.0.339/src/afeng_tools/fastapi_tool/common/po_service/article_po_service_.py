from typing import Any

from afeng_tools.fastapi_tool.common.po_service.base_po_service import PoService
from afeng_tools.fastapi_tool.common.service import icon_base_service
from afeng_tools.pydantic_tool.model.common_models import LinkItem


class ArticlePoService(PoService):
    """
    使用示例：article_po_service = ArticlePoService(app_info.db_code, ArticleInfoPo)
    """
    _table_name_ = "tb_article_info"

    def get_by_code(self, article_code: str, type_code: str = None) -> Any:
        if type_code:
            return self.get(self.model_type.type_code == type_code, self.model_type.code == article_code)
        return self.get(self.model_type.code == article_code)

    @classmethod
    def convert_to_link_item(cls, article_po, is_active: bool = False,
                             article_href_prefix: str = '/article') -> LinkItem:
        image_code = None
        if hasattr(article_po, 'icon_type') and hasattr(article_po, 'icon_value'):
            image_code = icon_base_service.get_icon_code(icon_type=article_po.icon_type,
                                                         icon_value=article_po.icon_value,
                                                         alt=article_po.title,
                                                         image_src=article_po.image_src)
        return LinkItem(
            target='_blank',
            title=article_po.title,
            href=f'{article_href_prefix}/{article_po.type_code}/{article_po.code}',
            code=article_po.code,
            description=article_po.description,
            image=image_code,
            is_active=is_active)


class ArticleDetailPoService(PoService):
    """
    使用示例：article_detail_po_service = ArticleDetailPoService(app_info.db_code, ArticleDetailInfoPo)
    """
    _table_name_ = "tb_article_detail_info"

    def get_by_id(self, article_id: int) -> Any:
        return self.get(self.model_type.article_id == article_id)

