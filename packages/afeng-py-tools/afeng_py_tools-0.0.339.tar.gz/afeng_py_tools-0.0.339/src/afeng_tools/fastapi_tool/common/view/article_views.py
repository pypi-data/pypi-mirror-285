from typing import Callable

from starlette.requests import Request

from afeng_tools.application_tool.application_models import AppInfo
from afeng_tools.fastapi_tool import fastapi_router_tools
from afeng_tools.fastapi_tool.template import template_service
from afeng_tools.fastapi_tool.template.item import ArticleTemplateItem


class ArticleView:
    """
    使用示例：router = ArticleView(app_info.db_code, ResourceInfoPo).router
    """

    def __init__(self, app_info: AppInfo,
                 detail_context_func: Callable[[Request, str], ArticleTemplateItem] = None,
                 type_context_func: Callable[[Request, str, str], ArticleTemplateItem] = None,
                 detail_page_template: str = '{app_code}/views/detail/index.html',
                 type_page_template: str = '{app_code}/views/{type_code}/index.html'):
        """
        是否缓存页面
        :param app_info:
        :param detail_context_func: 详情页内容函数(request, article_code)
        :param type_context_func: 类型页内容函数(request, type_code, article_code)
        :param detail_page_template: 详情页模板, 默认是：   '{app_code}/views/detail/index.html'
        :param type_page_template: 类型页模板，默认是：'{app_code}/views/{type_code}/index.html'
        """
        self.app_info = app_info
        self.detail_context_func = detail_context_func
        self.type_context_func = type_context_func
        self.detail_page_template = detail_page_template
        self.type_page_template = type_page_template
        self._router = fastapi_router_tools.create_router(prefix='/article', tags=['文章'])
        if detail_context_func:
            self._router.get('/detail/{article_code}')(self.detail_page)
        if type_context_func:
            self._router.get('/{type_code}/{article_code}')(self.type_page)

    @property
    def router(self):
        return self._router

    async def detail_page(self, request: Request, article_code: str):
        return template_service.render_template(request,
                                                template_file=self.detail_page_template.format(
                                                    app_code=self.app_info.code),
                                                template_item=self.detail_context_func(request, article_code))

    async def type_page(self, request: Request, type_code: str, article_code: str):
        return template_service.render_template(request,
                                                template_file=self.type_page_template.format(
                                                    app_code=self.app_info.code,
                                                    type_code=type_code),
                                                template_item=self.type_context_func(request, type_code, article_code))
