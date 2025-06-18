"""
系统日志模块，提供日志记录功能
支持不同级别的日志记录(info/error/warning/debug/critical)
日志会自动保存到指定目录的日期文件中
"""

import logging
import os
from datetime import datetime
import config
import pytz

def customTime(*args):
    """
    自定义时间格式化函数
    Returns:
        当前上海时区的时间元组
    """
    return datetime.now(pytz.timezone('Asia/Shanghai')).timetuple()

# 全局logger实例，初始化时为None
logger = None

def init_logger():
    """
    初始化日志系统
    配置日志级别、输出格式和处理器(文件和控制台)
    """
    global logger
    if logger is None:
        # 创建logger实例
        logger = logging.getLogger("系统日志log")
        # 设置日志级别为DEBUG(记录所有级别日志)
        logger.setLevel(logging.DEBUG)  

        # 创建日志目录(如果不存在)
        log_directory = config.logs_path
        os.makedirs(log_directory, exist_ok=True)

        # 使用当前日期作为日志文件名
        log_filename = datetime.now().strftime("%Y-%m-%d.log")

        # 文件处理器 - 记录INFO及以上级别的日志到文件
        fh = logging.FileHandler(os.path.join(log_directory, log_filename), encoding='utf-8')
        fh.setLevel(logging.INFO)

        # 控制台处理器 - 只记录ERROR及以上级别的日志到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)

        # 定义日志格式: 时间 - 名称 - 级别 - 消息
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # 使用上海时区的时间格式
        formatter.converter = customTime  
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 添加处理器到logger
        logger.addHandler(fh)
        logger.addHandler(ch)
        # 记录系统启动日志
        logger.info(f"系统启动时间: {customTime()}")

def log_message(status, message):
    """
    记录日志消息
    Args:
        status: 日志级别(info/error/warning/debug/critical)
        message: 要记录的日志内容
    """
    if status == 'info':
        logger.info(message)
    elif status == 'error':
        logger.error(message)
    elif status == 'warning':
        logger.warning(message)
    elif status == 'debug':
        logger.debug(message)
    elif status == 'critical':
        logger.critical(message)

# 模块加载时自动初始化logger
init_logger()

if __name__ == '__main__':
    # 模块测试代码 - 记录各种级别的日志
    log_message('info', '这是测试日志info')
    log_message('error', '这是测试日志error')
    log_message('debug', '这是测试日志debug')
    log_message('warning', '这是测试日志warning')
    log_message('critical', '这是测试日志critical')