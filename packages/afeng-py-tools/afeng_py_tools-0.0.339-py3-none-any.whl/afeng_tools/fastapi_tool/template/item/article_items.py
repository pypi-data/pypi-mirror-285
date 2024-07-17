from typing import Optional

from pydantic import BaseModel, Field


class ArticleInfoItem(BaseModel):
    """文章信息项"""
    type_code: Optional[str] = Field(title='类型编码', default=None)
    code: str = Field(title='编码')
    title: str = Field(title='标题')
    sub_title: Optional[str] = Field(title='副标题', default=None)
    description: Optional[str] = Field(title='简介', default=None)
    publish_time: Optional[str] = Field(title='发布时间', default=None)


class ArticleDetailInfoItem(ArticleInfoItem):
    """文章详情信息项"""
    content: Optional[str] = Field(title='内容', default=None)
