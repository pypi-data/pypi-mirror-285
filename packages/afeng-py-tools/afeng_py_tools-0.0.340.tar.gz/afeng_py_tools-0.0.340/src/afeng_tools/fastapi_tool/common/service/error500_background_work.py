import logging
from abc import ABCMeta

from starlette.requests import Request


class Error500BackgroundWork(metaclass=ABCMeta):
    app_title: str = None

    async def run(self, request: Request, exception: Exception, traceback_msg: str):
        if self.app_title:
            logging.error(f'[{self.app_title}]{traceback_msg}')
        else:
            logging.error(traceback_msg)
