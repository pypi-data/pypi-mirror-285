from afeng_tools.fastapi_tool.common.po_service.article_po_service_ import ArticlePoService, ArticleDetailPoService
from afeng_tools.fastapi_tool.common.po_service.blacklist_po_service_ import BlacklistPoService
from afeng_tools.fastapi_tool.common.po_service.category_po_service_ import CategoryPoService
from afeng_tools.fastapi_tool.common.po_service.count_po_service import CountPoService
from afeng_tools.fastapi_tool.common.po_service.group_po_service_ import GroupPoService
from afeng_tools.fastapi_tool.common.po_service.latest_update_po_service import LatestUpdatePoService
from afeng_tools.fastapi_tool.common.po_service.link_po_service_ import LinkPoService
from afeng_tools.fastapi_tool.common.po_service.relation_po_service_ import RelationPoService
from afeng_tools.fastapi_tool.common.po_service.resource_po_service_ import ResourcePoService
from afeng_tools.fastapi_tool.common.po_service.sitemap_po_service_ import SitemapPoService
from afeng_tools.fastapi_tool.common.po_service.tag_po_service_ import TagPoService, TagRelationPoService
from afeng_tools.fastapi_tool.common.po_service.tmp_po_service_ import TmpSortPoService


class CommonPoService:
    """通用po服务"""

    def __init__(self, db_code: str):
        self.db_code = db_code

        self._group_po_service = None
        self._category_po_service = None
        self._link_po_service = None
        self._resource_po_service = None
        self._tag_po_service = None
        self._tag_relation_po_service = None
        self._article_po_service = None
        self._article_detail_po_service = None
        self._relation_po_service = None
        self._blacklist_po_service = None
        self._tmp_sort_po_service = None
        self._sitemap_po_service = None
        self._count_po_service = None
        self._latest_update_po_service = None

    @property
    def group_po_service(self) -> GroupPoService:
        if self._group_po_service is None:
            self._group_po_service = GroupPoService(self.db_code)
        return self._group_po_service

    @property
    def category_po_service(self) -> CategoryPoService:
        if self._category_po_service is None:
            self._category_po_service = CategoryPoService(self.db_code)
        return self._category_po_service

    @property
    def link_po_service(self) -> LinkPoService:
        if self._link_po_service is None:
            self._link_po_service = LinkPoService(self.db_code)
        return self._link_po_service

    @property
    def resource_po_service(self) -> ResourcePoService:
        if self._resource_po_service is None:
            self._resource_po_service = ResourcePoService(self.db_code)
        return self._resource_po_service

    @property
    def tag_po_service(self) -> TagPoService:
        if self._tag_po_service is None:
            self._tag_po_service = TagPoService(self.db_code)
        return self._tag_po_service

    @property
    def tag_relation_po_service(self) -> TagRelationPoService:
        if self._tag_relation_po_service is None:
            self._tag_relation_po_service = TagRelationPoService(self.db_code)
        return self._tag_relation_po_service

    @property
    def article_po_service(self) -> ArticlePoService:
        if self._article_po_service is None:
            self._article_po_service = ArticlePoService(self.db_code)
        return self._article_po_service

    @property
    def article_detail_po_service(self) -> ArticleDetailPoService:
        if self._article_detail_po_service is None:
            self._article_detail_po_service = ArticleDetailPoService(self.db_code)
        return self._article_detail_po_service

    @property
    def relation_po_service(self) -> RelationPoService:
        if self._relation_po_service is None:
            self._relation_po_service = RelationPoService(self.db_code)
        return self._relation_po_service

    @property
    def blacklist_po_service(self) -> BlacklistPoService:
        if self._blacklist_po_service is None:
            self._blacklist_po_service = BlacklistPoService(self.db_code)
        return self._blacklist_po_service

    @property
    def tmp_sort_po_service(self) -> TmpSortPoService:
        if self._tmp_sort_po_service is None:
            self._tmp_sort_po_service = TmpSortPoService(self.db_code)
        return self._tmp_sort_po_service

    @property
    def sitemap_po_service(self) -> SitemapPoService:
        if self._sitemap_po_service is None:
            self._sitemap_po_service = SitemapPoService(self.db_code)
        return self._sitemap_po_service

    @property
    def count_po_service(self) -> CountPoService:
        if self._count_po_service is None:
            self._count_po_service = CountPoService(self.db_code)
        return self._count_po_service

    @property
    def latest_update_po_service(self) -> LatestUpdatePoService:
        if self._latest_update_po_service is None:
            self._latest_update_po_service = LatestUpdatePoService(self.db_code)
        return self._latest_update_po_service
