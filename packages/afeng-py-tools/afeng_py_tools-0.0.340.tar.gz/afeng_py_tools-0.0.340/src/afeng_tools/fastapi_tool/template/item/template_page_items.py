from typing import Any, Optional

from pydantic import BaseModel


class PageTemplateItem(BaseModel):
    """页面模板项"""
    is_mobile: Optional[bool] = False
    # 页面html中head标签元素
    html_head_template: Optional[str] = None
    # 页面头部模板
    page_header_template: Optional[str] = None
    # 页面底部模板
    page_footer_template: Optional[str] = None
    data_dict: Optional[dict[str, Any]] = None


class ArticleTemplateItem(PageTemplateItem):
    # 面包屑模板
    bread_crumb_template: Optional[str] = None
    # 左侧导航模板
    left_nav_template: Optional[str] = None
    # 文章标题
    title: Optional[str] = None
    # 文章副标题
    sub_title: Optional[str] = None
    # 文章内容
    content: Optional[str] = None
    # 元数据
    meta_data: Optional[dict[str, Any]] = None
