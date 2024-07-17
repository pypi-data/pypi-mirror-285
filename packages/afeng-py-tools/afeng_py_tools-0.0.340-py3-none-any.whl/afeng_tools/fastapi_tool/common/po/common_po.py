from sqlalchemy import BigInteger, Column, Text, String, Enum, Boolean, DateTime, func, Float, Integer

from afeng_tools.fastapi_tool.common.enum import IconTypeEnum, ResourceFormatEnum, SitemapFreqEnum, LinkTargetEnum
from afeng_tools.sqlalchemy_tools.core import sqlalchemy_base_model


class CountMixin:
    """数量Mixin"""
    _count: int = 0

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, count_value):
        self._count = count_value


class CommonPo:
    """
    通用模型: 使用示例：
        common_po = CommonPo(db_code=app_info.db_code)
        GroupInfoPo, CategoryInfoPo, ResourceInfoPo, LinkInfoPo, TagInfoPo, BlacklistInfoPo, SitemapInfoPo, ArticleInfoPo,ArticleDetailInfoPo = (common_po.GroupInfoPo, common_po.CategoryInfoPo, common_po.ResourceInfoPo, common_po.LinkInfoPo, common_po.TagInfoPo,common_po.BlacklistInfoPo, common_po.SitemapInfoPo,
                                            common_po.ArticleInfoPo, common_po.ArticleDetailInfoPo)
    """

    def __init__(self, db_code: str):
        self.db_code = db_code
        self.BaseModel = sqlalchemy_base_model.get_base_model(db_code=db_code)
        self._GroupInfoPo = None
        self._CategoryInfoPo = None
        self._ResourceInfoPo = None
        self._LinkInfoPo = None
        self._TagInfoPo = None
        self._TagRelationInfoPo = None
        self._BlacklistInfoPo = None
        self._SitemapInfoPo = None
        self._ArticleInfoPo = None
        self._ArticleDetailInfoPo = None
        self._CountInfoPo = None
        self._TmpSortInfoPo = None
        self._RelationInfoPo = None
        self._LatestUpdateInfoPo = None

    @property
    def GroupInfoPo(self):
        if self._GroupInfoPo is not None:
            return self._GroupInfoPo

        class GroupInfoPo(self.BaseModel, CountMixin):
            """分组信息"""
            __tablename__ = "tb_group_info"
            type_code = Column(String(100), comment='类型编码', default='default', unique=False, nullable=True)
            code = Column(String(100), comment='编码', unique=True, nullable=True, index=True)
            title = Column(String(255), comment='标题', unique=False, nullable=True)
            description = Column(Text, comment='描述', unique=False, nullable=True)
            image_src = Column(Text, comment='图标源地址', unique=False, nullable=True)
            icon_type = Column(Enum(IconTypeEnum, values_callable=lambda x: [i.value.value for i in x]),
                               comment='图标类型',
                               unique=False, nullable=True)
            icon_value = Column(Text, comment='图标值', unique=False, nullable=True)

        self._GroupInfoPo = GroupInfoPo
        return self._GroupInfoPo

    @property
    def CategoryInfoPo(self):
        if self._CategoryInfoPo is not None:
            return self._CategoryInfoPo

        class CategoryInfoPo(self.BaseModel, CountMixin):
            """分类信息"""
            __tablename__ = "tb_category_info"
            group_code = Column(String(100), comment='分组编码', unique=False, nullable=True)
            code = Column(String(100), comment='编码', unique=True, nullable=True, index=True)
            title = Column(String(255), comment='标题', unique=False, nullable=True)
            description = Column(Text, comment='描述', unique=False, nullable=True)
            image_src = Column(Text, comment='图标源地址', unique=False, nullable=True)
            icon_type = Column(Enum(IconTypeEnum, values_callable=lambda x: [i.value.value for i in x]),
                               comment='图标类型', unique=False, nullable=True)
            icon_value = Column(Text, comment='图标值', unique=False, nullable=True)
            parent_code = Column(String(100), comment='父编码', unique=False, nullable=True)

        self._CategoryInfoPo = CategoryInfoPo
        return self._CategoryInfoPo

    @property
    def ResourceInfoPo(self):
        if self._ResourceInfoPo is not None:
            return self._ResourceInfoPo

        class ResourceInfoPo(self.BaseModel):
            """资源信息"""
            __tablename__ = "tb_resource_info"
            type_code = Column(String(100), comment='类型编码', default='default', unique=False, nullable=True)
            resource_code = Column(String(100), comment='资源编码', index=True, unique=True, nullable=True)
            resource_name = Column(String(255), comment='资源名称', unique=False, nullable=True)
            resource_format = Column(Enum(ResourceFormatEnum), comment='资源格式（image:图片）', unique=False,
                                     nullable=True)
            local_path = Column(String(500), comment='本地路径', unique=False, nullable=True)
            baidu_fs_id = Column(BigInteger, comment='百度fs_id', unique=False, nullable=True)
            baidu_md5 = Column(String(255), comment='文件在百度网盘的md5', unique=False, nullable=True)
            baidu_size = Column(BigInteger, comment='在百度网盘的文件大小', unique=False, nullable=True)
            access_url = Column(String(500), comment='访问url', unique=False, nullable=True)
            expire_timestamp = Column(BigInteger, comment='过期时间戳', unique=False, nullable=True)
            download_flag = Column(Boolean, comment='下载标志', default=False)

        self._ResourceInfoPo = ResourceInfoPo
        return self._ResourceInfoPo

    @property
    def LinkInfoPo(self):
        if self._LinkInfoPo is not None:
            return self._LinkInfoPo

        class LinkInfoPo(self.BaseModel):
            """链接信息"""
            __tablename__ = "tb_link_info"
            type_code = Column(String(100), comment='类型编码', default='default', unique=False, nullable=True)
            code = Column(String(100), comment='编码', unique=True, nullable=True, index=True)
            title = Column(String(100), comment='标题', unique=False, nullable=True)
            description = Column(Text, comment='描述', unique=False, nullable=True)
            image_src = Column(Text, comment='图标源地址', unique=False, nullable=True)
            icon_type = Column(Enum(IconTypeEnum, values_callable=lambda x: [i.value.value for i in x]),
                               comment='图标类型', unique=False, nullable=True)
            icon_value = Column(Text, comment='图标值', unique=False, nullable=True)
            link_url = Column(String(500), comment='链接地址', unique=False, nullable=True)
            parent_code = Column(String(100), comment='父编码', unique=False, nullable=True)
            target = Column(Enum(LinkTargetEnum), comment='打开方式', default=LinkTargetEnum.blank, unique=False,
                            nullable=True)
            is_ok = Column(Boolean, comment='是否正常访问', default=True)

        self._LinkInfoPo = LinkInfoPo
        return self._LinkInfoPo

    @property
    def TagInfoPo(self):
        if self._TagInfoPo is not None:
            return self._TagInfoPo

        class TagInfoPo(self.BaseModel, CountMixin):
            """标签信息"""
            __tablename__ = "tb_tag_info"
            type_code = Column(String(100), comment='类型编码', default='default', unique=False, nullable=True)
            code = Column(String(100), comment='编码', unique=True, nullable=True, index=True)
            title = Column(String(100), comment='标题', unique=False, nullable=True)
            description = Column(String(255), comment='描述', unique=False, nullable=True)

        self._TagInfoPo = TagInfoPo
        return self._TagInfoPo

    @property
    def TagRelationInfoPo(self):
        if self._TagRelationInfoPo is not None:
            return self._TagRelationInfoPo

        class TagRelationInfoPo(self.BaseModel):
            """标签关联"""
            __tablename__ = "tb_tag_relation_info"
            tag_code = Column(String(100), comment='标签编码', unique=False, nullable=False)
            type_code = Column(String(100), comment='类型编码', default='default', unique=False, nullable=True)
            type_value = Column(String(255), comment='类型值', unique=False, nullable=True)

        self._TagRelationInfoPo = TagRelationInfoPo
        return self._TagRelationInfoPo

    @property
    def ArticleInfoPo(self):
        if self._ArticleInfoPo is not None:
            return self._ArticleInfoPo

        class ArticleInfoPo(self.BaseModel):
            """帮助信息"""
            __tablename__ = "tb_article_info"
            type_code = Column(String(100), comment='类型编码', default='default', unique=False, nullable=True)
            code = Column(String(100), comment='编码', unique=False, nullable=True, index=True)
            title = Column(String(255), comment='标题', unique=False, nullable=True)
            sub_title = Column(String(255), comment='副标题', unique=False, nullable=True)
            description = Column(String(336), comment='描述', unique=False, nullable=True)
            publish_time = Column(DateTime, comment='发布时间', default=func.now())

        self._ArticleInfoPo = ArticleInfoPo
        return self._ArticleInfoPo

    @property
    def ArticleDetailInfoPo(self):
        if self._ArticleDetailInfoPo is not None:
            return self._ArticleDetailInfoPo

        class ArticleDetailInfoPo(self.BaseModel):
            """帮助信息"""
            __tablename__ = "tb_article_detail_info"
            article_id = Column(BigInteger, comment='文章主键', index=True, unique=True, nullable=False)
            content = Column(Text, comment='内容', unique=False, nullable=True)

        self._ArticleDetailInfoPo = ArticleDetailInfoPo
        return self._ArticleDetailInfoPo

    @property
    def CountInfoPo(self):
        if self._CountInfoPo is not None:
            return self._CountInfoPo

        class CountInfoPo(self.BaseModel):
            """数量信息"""
            __tablename__ = "tb_count_info"
            type_code = Column(String(100), comment='类型编码', default='default', unique=False, nullable=True)
            type_value = Column(String(255), comment='类型值', unique=False, nullable=True)
            count_value = Column(BigInteger, comment='数量值', default=0, unique=False)

        self._CountInfoPo = CountInfoPo
        return self._CountInfoPo

    @property
    def RelationInfoPo(self):
        if self._RelationInfoPo is not None:
            return self._RelationInfoPo

        class RelationInfoPo(self.BaseModel):
            """关联信息"""
            __tablename__ = "tb_relation_info"
            relation_type = Column(String(100), comment='关联类型', unique=False, nullable=False)
            point_1 = Column(String(100), comment='关联点1', unique=False, nullable=True)
            point_2 = Column(String(100), comment='关联点2', unique=False, nullable=True)

        self._RelationInfoPo = RelationInfoPo
        return self._RelationInfoPo

    @property
    def TmpSortInfoPo(self):
        if self._TmpSortInfoPo is not None:
            return self._TmpSortInfoPo

        class TmpSortInfoPo(self.BaseModel):
            """临时排序信息信息"""
            __tablename__ = "tmp_sort_info"
            type_code = Column(String(100), comment='类型编码', default='default', unique=False, nullable=True)
            unique_code = Column(String(100), comment='唯一码', unique=False, nullable=True, index=True)
            sort_value = Column(String(100), comment='排序值', unique=False, nullable=True)
            sort_index = Column(Integer, comment='排序索引', unique=False, nullable=True)

        self._TmpSortInfoPo = TmpSortInfoPo
        return self._TmpSortInfoPo

    @property
    def BlacklistInfoPo(self):
        if self._BlacklistInfoPo is not None:
            return self._BlacklistInfoPo

        class BlacklistInfoPo(self.BaseModel):
            """黑名单信息"""
            __tablename__ = "tb_blacklist_info"
            type_code = Column(String(100), comment='类型编码', default='default', unique=False, nullable=True)
            type_value = Column(String(255), comment='类型值', unique=False, nullable=True)

        self._BlacklistInfoPo = BlacklistInfoPo
        return self._BlacklistInfoPo

    @property
    def SitemapInfoPo(self):
        if self._SitemapInfoPo is not None:
            return self._SitemapInfoPo

        class SitemapInfoPo(self.BaseModel):
            """站点地图信息"""
            __tablename__ = "tb_sitemap_info"
            type_code = Column(String(100), comment='类型编码', default='default', unique=False, nullable=True)
            title = Column(String(255), comment='标题', unique=False, nullable=True)
            loc_url = Column(String(500), comment='url地址', unique=False, nullable=True)
            # 0.0 ~ 1.0
            priority = Column(Float, comment='优先权', unique=False, nullable=True)
            last_mod = Column(String(100), comment='最新一次更新时间(YYYY-MM-DD或，YYYY-MM-DDThh:mm:ss)',
                              unique=False, nullable=True)
            change_freq = Column(Enum(SitemapFreqEnum), comment='更新频率',
                                 default=SitemapFreqEnum.daily, unique=False, nullable=True)
            parent_id = Column(BigInteger, comment='主键', unique=False, nullable=True)

        self._SitemapInfoPo = SitemapInfoPo
        return self._SitemapInfoPo

    @property
    def LatestUpdateInfoPo(self):
        if self._LatestUpdateInfoPo is not None:
            return self._LatestUpdateInfoPo

        class LatestUpdateInfoPo(self.BaseModel):
            """最新更新信息"""
            __tablename__ = "tb_latest_update_info"
            type_code = Column(String(100), comment='类型编码', default='default', unique=False, nullable=True)
            type_value = Column(String(255), comment='类型值', unique=False, nullable=True)
            update_time_value = Column(String(20), comment='最新更新时间', unique=False, nullable=True)
            link_url = Column(String(255), comment='最新更新资源的链接', unique=False, nullable=True)

        self._LatestUpdateInfoPo = LatestUpdateInfoPo
        return self._LatestUpdateInfoPo
