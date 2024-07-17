from typing import Optional, Any

from afeng_tools.pydantic_tool.model.common_models import LinkItem, EnumItem
from pydantic import BaseModel, Field

from afeng_tools.fastapi_tool.template.item import CalendarDataItem, AppinfoDataItem, Error501DataItem, \
    Error500DataItem, Error404DataItem, TemplateBaseData


class TemplateHtmlHeadData(TemplateBaseData):
    """模板head信息"""
    # 标题
    title: str
    # 描述
    description: Optional[str] = None
    # 关键字
    keyword_list: Optional[list[str]] = []
    # 作者
    author: Optional[str] = Field(default='chentiefeng')
    # favicon图标
    favicon: Optional[str] = Field(default='/favicon.ico')
    # 域信息
    origin: Optional[str] = None
    # 百度统计id
    baidu_tm_id: Optional[str] = None
    # 自定义 head部分代码列表
    custom_head_code_list: Optional[list[str]] = None


class TemplateBreadCrumbData(TemplateBaseData):
    """面包屑信息"""
    # 标题
    page_title: Optional[str] = None
    # 面包屑列表
    bread_crumb_list: Optional[list[LinkItem]] = None


class TemplateLeftNavData(TemplateBaseData):
    """左侧链接信息"""
    # 链接列表
    link_list: Optional[list[LinkItem]] = None


class TemplatePaginationAreaData(TemplateBaseData):
    """分页信息"""
    # 上一页按钮
    pre_btn: Optional[LinkItem] = None
    # 下一页按钮
    next_btn: Optional[LinkItem] = None
    # 中间数据按钮
    data_list: Optional[list[LinkItem]] = []
    # 是否显示数量区域
    is_show_count_area: Optional[bool] = True
    # 总数量
    total_count: Optional[int] = 0
    # 总页数
    total_page: Optional[int] = 0
    # 跳转到某页的地址
    jump_href: Optional[str] = None
    # 跳转页面时附加的数据数据字典
    jump_data_dict: Optional[dict[str, Any]] = None


class TemplatePageFooterData(TemplateBaseData):
    """页面底部链息"""
    # 友情链接标题
    friendly_link_title: Optional[LinkItem] = LinkItem(title='友情链接', href='/article/help/friendly_link')
    # 联系信息，如：QQ: 1640125562， 邮箱：imafengbook@aliyun.com
    contact_info: Optional[str] = None
    # 友情链接列表
    friendly_link_list: Optional[list[LinkItem]] = None
    # 底部链接列表
    footer_link_list: Optional[list[LinkItem]] = None
    # 版权链接
    copyright_link: Optional[LinkItem] = LinkItem(title='阿锋', href='/')
    # ICP备案信息，如：京ICP备2023032898号-1 京公网安备xxxx号
    icp_record_info: Optional[str] = None
    # 公安备案信息，如：京公网安备11000002000001号
    police_record_info: Optional[str] = None
    # 公安备案号：11000002000001
    police_record_code: Optional[str] = None


class TemplateTopBarData(TemplateBaseData):
    """页面顶部top bar链息"""
    have_home_btn: Optional[bool] = True
    # 应用信息
    app_info: Optional[AppinfoDataItem] = None
    # 应用链接列表
    app_link_list: Optional[list[LinkItem]] = None
    # 微信公众号图片
    weixin_qr_code_image: Optional[str] = '/static/image/qrcode/wx_of_qrcode.jpg'
    # 快捷链接列表
    quick_link_list: Optional[list[LinkItem]] = None


class TemplateLogoSearchData(TemplateBaseData):
    """页面顶部logo search链息"""
    # logo图片
    logo_image: Optional[str] = '/image/logo/logo.png'
    # 应用标题, 如：阿锋书屋
    app_title: Optional[str] = None
    # 查询表单提交url
    search_form_submit_url: Optional[str] = '/search'
    # 查询选项名称， 如：search_type
    search_select_type_name: Optional[str] = 'search_type'
    # 查询选项列表
    search_select_option_list: Optional[list[EnumItem]] = None


class TemplateFixNavData(TemplateBaseData):
    """页面顶部fix nav链息"""
    # 类型链接列表
    type_link_list: Optional[list[LinkItem]] = None
    # 热点链接列表
    hotspot_link_list: Optional[list[LinkItem]] = None


class TemplatePageHeaderData(TemplateBaseData):
    """页面顶部链息"""
    # topbar数据
    topbar_data: Optional[TemplateTopBarData] = None
    # logo search数据
    logo_search_data: Optional[TemplateLogoSearchData] = None
    # fix nav数据
    fix_nav_data: Optional[TemplateFixNavData] = None


class TemplateIndexPageHeaderData(TemplateBaseData):
    """首页页面顶部链息"""
    # 应用链接列表
    app_link_list: Optional[list[LinkItem]] = None
    # 微信公众号图片
    weixin_qr_code_image: Optional[str] = '/static/image/qrcode/wx_of_qrcode.jpg'
    # 快捷链接列表
    quick_link_list: Optional[list[LinkItem]] = None
    # 全部类型列表
    all_type_list: Optional[list[LinkItem]] = None


class TemplatePageSearchHeaderData(TemplateBaseData):
    """搜索页面顶部数据"""
    # 微信公众号图片
    weixin_qr_code_image: Optional[str] = '/static/image/qrcode/wx_of_qrcode.jpg'
    # 快捷链接列表
    quick_link_list: Optional[list[LinkItem]] = None
    # 查询关键字
    keyword: Optional[str] = None
    # 搜索模式
    search_model_list: Optional[list[EnumItem]] = None
    # 搜索类型
    search_type_list: Optional[list[EnumItem]] = None


class TemplateResultListData(TemplateBaseData):
    """页面结果列表链息"""
    # 结果值列表
    data_list: Optional[list[Any]] = None
    # 没有数据时的html代码
    none_html_code: Optional[str] = '暂无数据！'


class TemplateGroupListData(TemplateBaseData):
    """分组列表模块数据"""
    # 查询提交url
    search_url: Optional[str] = None
    # 查询输入框placeholder
    search_placeholder: Optional[str] = None
    # 搜索值
    search_value: Optional[str] = None
    # 数据列表
    data_list: Optional[list[LinkItem]] = None


class TemplateTagListData(TemplateBaseData):
    """标签列表模块数据"""
    # 查询提交url
    search_url: Optional[str] = None
    # 查询输入框placeholder
    search_placeholder: Optional[str] = None
    # 搜索值
    search_value: Optional[str] = None
    # 数据列表
    data_list: Optional[list[LinkItem]] = None


class TemplateFilterTypeAreaData(TemplateBaseData):
    """过滤模块区域数据"""
    # 数据列表
    data_list: Optional[list[LinkItem]] = None


class TemplateDayCalendarData(TemplateBaseData):
    """日历模块数据"""
    # 标题
    title: Optional[str] = None
    # 初始日期
    init_date: Optional[str] = None
    # 数据列表
    data_list: Optional[list[CalendarDataItem]] = None


class TemplateTabPanelItem(BaseModel):
    """Tab标签模块item数据"""
    # 是否激活
    is_active: Optional[bool] = False
    # 编码
    code: Optional[str] = None
    # 标题
    title: Optional[str] = None
    # html内容
    html: Optional[str] = None


class TemplateTabPanelData(TemplateBaseData):
    """Tab标签模块数据"""
    # 查看更多的按钮
    more_btn: Optional[LinkItem] = None
    # 子项列表
    item_list: Optional[list[TemplateTabPanelItem]] = None


class TemplateTopRankingData(TemplateBaseData):
    """排行榜模块数据"""
    # 标题
    title: Optional[str] = None
    # 数据列表
    data_list: Optional[list[LinkItem]] = None


class TemplateRedirectDownloadAreaData(TemplateBaseData):
    """重定向下载区域数据"""
    # 应用信息
    app_info: Optional[AppinfoDataItem] = None
    # 文件名
    file_name: Optional[str] = None
    # 广告列表
    ad_list: Optional[list[LinkItem]] = None
    # 下载链接
    download_url: Optional[str] = None
    # 返回链接
    back_url: Optional[str] = '/'


class TemplateRedirectAreaData(TemplateBaseData):
    """重定向区域数据"""
    # 应用信息
    app_info: Optional[AppinfoDataItem] = None
    # 广告列表
    ad_list: Optional[list[LinkItem]] = None
    # 跳转链接
    redirect_url: Optional[str] = None
    # 返回链接
    back_url: Optional[str] = '/'


class TemplateInfoAreaData(TemplateBaseData):
    """信息展示区域数据"""
    # 应用信息
    app_info: Optional[AppinfoDataItem] = None
    # 广告列表
    ad_list: Optional[list[LinkItem]] = None
    # 标题
    title: Optional[str] = None
    # 数据列表
    data_list: Optional[list[LinkItem]] = None


class TemplateShowQrcodeAreaData(TemplateBaseData):
    """显示二维码区域数据"""
    # 二维码图片地址
    qrcode_image_url: Optional[str] = '/static/image/qrcode/wx_of_qrcode.jpg'
    # 二维码图片标题
    qrcode_image_title: Optional[str] = None
    # 提示信息列表
    message_list: Optional[list[str]] = None


class TemplateAlertInfoAreaData(TemplateBaseData):
    """重定向区域数据"""
    # 警告图标前端代码
    alert_logo_url: Optional[
        str] = 'data:image/svg+xml;base64,PHN2ZyB0PSIxNzEzODQ4NjkwODEzIiBjbGFzcz0iaWNvbiIgdmlld0JveD0iMCAwIDEwMjQgMTAyNCIgdmVyc2lvbj0iMS4xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHAtaWQ9IjE0NTYiIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIj48cGF0aCBkPSJNNTEyLjIxNjgzIDAuMDM4MTU0QzIyOS45NDM4MTMgMC4wMzgxNTQgMS4xMTg5NDkgMjI5LjExODQwNCAxLjExODk0OSA1MTEuNzA2NDU3IDEuMTE4OTQ5IDc5NC4yOTQ1MTEgMjI5Ljk0MzgxMyAxMDIzLjM3NDc2MyA1MTIuMjE2ODMgMTAyMy4zNzQ3NjMgNzk0LjQ4OTg0NSAxMDIzLjM3NDc2MyAxMDIzLjMxNDcxMSA3OTQuMjk0NTExIDEwMjMuMzE0NzExIDUxMS43MDY0NTcgMTAyMy4zMTQ3MTEgMjI5LjExODQwNCA3OTQuNDg5ODQ1IDAuMDM4MTU0IDUxMi4yMTY4MyAwLjAzODE1NEw1MTIuMjE2ODMgMC4wMzgxNTRaTTUxMi4yMTY4MyA4MzEuNTAwNzU0QzQ3Ni45MzE2ODEgODMxLjUwMDc1NCA0NDguMzI5NzQxIDgwMi44NjY4OTMgNDQ4LjMyOTc0MSA3NjcuNTQyMzYzIDQ0OC4zMjk3NDEgNzMyLjIxNzgzMyA0NzYuOTMxNjgxIDcwMy41ODM5NzIgNTEyLjIxNjgzIDcwMy41ODM5NzIgNTQ3LjUwMTk3OSA3MDMuNTgzOTcyIDU3Ni4xMDM5MTkgNzMyLjIxNzgzMyA1NzYuMTAzOTE5IDc2Ny41NDIzNjMgNTc2LjEwMzkxOSA4MDIuODY2ODkzIDU0Ny41MDE5NzkgODMxLjUwMDc1NCA1MTIuMjE2ODMgODMxLjUwMDc1NEw1MTIuMjE2ODMgODMxLjUwMDc1NFpNNTc2LjEwNTA4NSA1NzUuNjY2MDE3QzU3Ni4xMDUwODUgNjEwLjk5MDU0NiA1NDcuNTAzMTQ3IDYzOS42MjQ0MDggNTEyLjIxNzk5OCA2MzkuNjI0NDA4IDQ3Ni45MzI4NDggNjM5LjYyNDQwOCA0NDguMzMwOTA4IDYxMC45OTA1NDYgNDQ4LjMzMDkwOCA1NzUuNjY2MDE3TDQ0OC4zMzA5MSAyNTUuODcyODlDNDQ4LjMzMDkxIDIyMC41NDgzNiA0NzYuOTMyODQ5IDE5MS45MTQ0OTggNTEyLjIxNzk5OSAxOTEuOTE0NDk4IDU0Ny41MDMxNDggMTkxLjkxNDQ5OCA1NzYuMTA1MDkxIDIyMC41NDgzNiA1NzYuMTA1MDkxIDI1NS44NzI4OUw1NzYuMTA1MDg1IDU3NS42NjYwMTcgNTc2LjEwNTA4NSA1NzUuNjY2MDE3WiIgZmlsbD0iI0RDNEYyQyIgcC1pZD0iMTQ1NyI+PC9wYXRoPjwvc3ZnPg=='
    # 警告标题
    alert_title: Optional[str] = '警告'
    # 提示信息列表
    alert_message_list: list[str]


class TemplateError404AreaData(TemplateBaseData, Error404DataItem):
    """错误404数据"""
    pass


class TemplateError500AreaData(TemplateBaseData, Error500DataItem):
    """错误500数据"""
    pass


class TemplateError501AreaData(TemplateBaseData, Error501DataItem):
    """错误501数据"""
    pass
