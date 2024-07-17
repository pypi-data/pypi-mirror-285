from typing import Any, Optional
from pydantic import BaseModel, Field

from afeng_tools.pydantic_tool.model.common_models import LinkItem


class TemplateBaseData(BaseModel):
    """模板基础数据"""
    # 是否是移动端
    is_mobile: Optional[bool] = False
    # 附加的数据字典
    data_dict: Optional[dict[str, Any]] = None


class PageDataItem(BaseModel):
    """分页数据项"""
    # 当前页
    current_page: Optional[int] = 1
    # 分页大小
    page_size: Optional[int] = 10
    # 总数量
    total_count: Optional[int] = 0
    # 总页数
    total_page: Optional[int] = 0
    # 数据列表
    data_list: Optional[list[Any]] = None


class SearchResultItem(BaseModel):
    """搜索结果项"""
    # 索引值
    index: Optional[int] = None
    # 封面图代码
    cover_image_code: Optional[str] = None
    # 标题
    title: Optional[str] = None
    # 链接
    href: Optional[str] = None
    # 简介
    description: Optional[str] = None
    # 分类标题
    category_title: Optional[str] = None
    # 分类的链接
    category_href: Optional[str] = None
    # 更新日期
    update_date: Optional[str] = None
    # 更新日期链接
    update_date_href: Optional[str] = None
    # 额外数据
    data_dict: Optional[dict[str, Any]] = None


class SearchResultAreaData(TemplateBaseData):
    # 结果值列表
    item_list: Optional[list[SearchResultItem]] = None
    # 没有数据时的html代码
    none_html_code: Optional[str] = '暂无数据！'


class CalendarDataItem(BaseModel):
    """日历项"""
    date: Optional[str] = Field(title='日期', default=None)
    value: Optional[Any] = Field(title='数据', default=None)
    href: Optional[str] = Field(title='链接地址', default=None)


class AppinfoDataItem(BaseModel):
    # 应用标题
    title: Optional[str] = None
    # logo图片
    logo_image: Optional[str] = '/static/image/logo/logo.png'
    # 应用链接
    url: Optional[str] = '/'
    # 百度统计id
    baidu_tm_id: Optional[str] = None


class Error404DataItem(BaseModel):
    """错误404数据"""
    # 页面标题
    title: Optional[str] = '404-Not Found'
    # 错误信息
    message: Optional[str] = '很抱歉，找不到网页！'
    # 子消息
    sub_message: Optional[str] = '您访问的页面不存在或已被删除！ (｡•ˇ‸ˇ•｡)'


class Error500DataItem(BaseModel):
    """错误500数据"""
    # 页面标题
    title: Optional[str] = '500-服务器错误'
    # 错误信息
    message: Optional[str] = '服务器内部错误（Internal Server Error）'
    # 子消息
    sub_message: Optional[str] = '当您看到这个页面，表示服务器内部错误，此网站可能遇到技术问题，无法执行您的请求，请稍后重试或联系管理员进行处理，感谢您的支持！'
    # 等待秒数
    wait_seconds: Optional[int] = 30
    # 管理员联系方式， 如：mailto:afengbook@aliyun.com
    contact_info_url: Optional[str] = None


class Error501DataItem(BaseModel):
    """错误501数据"""
    # 页面标题
    title: Optional[str] = '501-操作失败'
    # 错误信息，如：很抱歉，无法完成您的操作
    message: Optional[str] = '操作失败'
    # 子消息， 如：很抱歉，无法完成您的操作，请进行<a href="https://txc.qq.com/products/622359" target="_blank">问题反馈</a>，感谢您的支持！
    sub_message: Optional[str] = '如果要解决该问题，请进行问题反馈，感谢您的支持！'
    # 管理员联系方式， 如：mailto:afengbook@aliyun.com
    contact_info_url: Optional[str] = None
    # 问题反馈链接, 如：https://txc.qq.com/products/622359
    feedback_url: Optional[str] = None


class RankingAreaTemplateItem(TemplateBaseData):
    """排行榜区域模板项"""
    # 区域标题
    title: Optional[str] = None
    # 更多按钮
    more_btn: Optional[LinkItem] = None
    # 列表项
    item_list: Optional[list[LinkItem]] = None


class HotTagAreaTemplateItem(TemplateBaseData):
    """热点标签区域模板项"""
    # 区域标题
    title: Optional[str] = None
    # 更多按钮
    more_btn: Optional[LinkItem] = None
    # 列表项
    item_list: Optional[list[LinkItem]] = None


class RecentItem(LinkItem):
    """最近更新项"""
    # 类型
    type_item: Optional[LinkItem] = None
    time_item: Optional[LinkItem] = None


class RecentAreaTemplateItem(TemplateBaseData):
    """最近更新区域模板项"""
    # 区域标题
    title: Optional[str] = None
    # 更多按钮
    more_btn: Optional[LinkItem] = None
    # 列表项
    item_list: Optional[list[RecentItem]] = None


class SliderItem(LinkItem):
    """轮播项"""
    # 图片地址
    image_src: Optional[str] = None


class TemplateSliderWithTitleAreaData(TemplateBaseData):
    """页面带有标题的轮播图链息"""
    item_list: Optional[list[SliderItem]] = None


class FilterItem(BaseModel):
    title: Optional[str] = None
    # 类型列表
    type_list: Optional[list[LinkItem]] = None


class FilterAllTypeAreaData(TemplateBaseData):
    """过滤类型区域数据"""
    item_list: Optional[list[FilterItem]] = None


class FilterSortAreaData(TemplateBaseData):
    pass
