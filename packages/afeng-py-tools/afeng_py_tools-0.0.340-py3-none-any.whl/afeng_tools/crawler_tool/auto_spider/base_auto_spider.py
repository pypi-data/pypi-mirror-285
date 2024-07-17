import os
from abc import ABCMeta, abstractmethod
from playwright.sync_api import Page

from afeng_tools.encryption_tool import hashlib_tools
from afeng_tools.file_tool import tmp_file_tools
from afeng_tools.log_tool import loguru_tools
from afeng_tools.playwright_tool import http_header_tools, http_cookie_tools
from afeng_tools.playwright_tool.decorator.playwright_decorators import auto_input

logger = loguru_tools.get_logger()


class BaseAutoSpider(metaclass=ABCMeta):
    """自动化爬虫基类"""
    # 爬虫编码
    spider_code: str = None
    # 是否headless
    headless: bool = False

    def __init__(self):
        if not self.spider_code:
            self.spider_code = hashlib_tools.calc_md5(__file__)
        auth_save_path = os.path.join(tmp_file_tools.get_user_tmp_dir(), 'spider_auth-file')
        os.makedirs(auth_save_path, exist_ok=True)
        self.cookie_file = os.path.join(auth_save_path, f'{self.spider_code}-cookie.txt')
        self.header_file = os.path.join(auth_save_path, f'{self.spider_code}-header.txt')

    def _refresh_auth(self, web_page: Page):
        """刷新认证"""
        logger.info('[登录]进入登录逻辑')
        self.login(web_page=web_page)
        logger.info('[登录]登录完成')
        logger.info('[保存]认证header')
        http_header_tools.save_headers(web_page, self.header_file)
        logger.info('[保存]认证cookie')
        http_cookie_tools.save_cookies(web_page, self.cookie_file)

    def _load_auth_file(self, web_page: Page):
        """加载认证文件"""
        if not os.path.exists(self.cookie_file) or not os.path.exists(self.header_file):
            self._refresh_auth(web_page=web_page)
        return self.header_file, self.cookie_file

    def load_auth(self, web_page: Page):
        """加载认证"""
        logger.info('加载认证信息')
        header_file, cookie_file = self._load_auth_file(web_page)
        http_header_tools.set_headers(page=web_page, auth_header_file=header_file)
        http_cookie_tools.set_cookies(page=web_page, auth_cookie_file=cookie_file)

    def login(self, web_page: Page):
        """登录逻辑：如果需要登录，则需要实现该方法"""
        raise NotImplementedError('没有继承实现登录逻辑，无法进行认证操作！')

    @abstractmethod
    @auto_input(headless=headless)
    def run(self, web_page: Page = None, **kwargs):
        pass
