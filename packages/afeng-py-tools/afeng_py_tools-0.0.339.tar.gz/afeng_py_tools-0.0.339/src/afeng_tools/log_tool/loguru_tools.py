"""
loguru工具类： pip install loguru  -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""
import traceback

from loguru import logger

from afeng_tools.log_tool import logger_settings
from afeng_tools.log_tool.logger_enums import LoggerConfigKeyEnum


def get_logger():
    info_file = logger_settings.get_config(LoggerConfigKeyEnum.info_file)
    info_rotation = logger_settings.get_config(LoggerConfigKeyEnum.info_rotation)
    if not info_rotation:
        info_rotation = '50 MB'
    if info_file:
        logger.add(info_file, rotation=info_rotation, compression='zip', encoding='utf-8', level='INFO')
    error_file = logger_settings.get_config(LoggerConfigKeyEnum.error_file)
    error_rotation = logger_settings.get_config(LoggerConfigKeyEnum.error_rotation)
    if not error_rotation:
        error_rotation = '30 MB'
    if error_file:
        logger.add(error_file, rotation=error_rotation, compression='zip', encoding='utf-8', level='WARNING')
    return logger


def log_error(log, error_msg: str, ex: Exception = None):
    """记录错误日志"""
    if ex:
        log.error(f'{error_msg}:{ex}\n {traceback.format_exc()}')
    else:
        log.error(f'{error_msg}\n {traceback.format_exc()}')
