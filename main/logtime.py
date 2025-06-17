import logging
import os
from datetime import datetime, timezone, timedelta
import config


# 初始化logger
logger = None

def init_logger():
    global logger
    if logger is None:
        logger = logging.getLogger("系统日志")
        logger.setLevel(logging.DEBUG)

        # 指定日志文件的目录
        log_directory = config.logs_path

        # 确保日志目录存在，不存在则创建
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        # 使用当前时间创建日志文件名
        log_filename = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d.log")

        # 创建一个handler用于写入日志文件
        fh = logging.FileHandler(os.path.join(log_directory, log_filename), encoding='utf-8')
        fh.setLevel(logging.DEBUG)

        # 创建一个handler用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)  # 调整为INFO级别

        # 定义handler的输出格式 , 记录系统启动时间
        # 格式化输出时间，使用当前时间，并调整时区为北京时间
        startup_time = datetime.now(timezone(timedelta(hours=8)))
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt=startup_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            )

        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        logger.addHandler(fh)
        logger.addHandler(ch)
        logger.info(f"系统启动时间: {startup_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")


def log_message(status, message):
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

# 初始化logger
init_logger()

if __name__ == '__main__':
    # 记录日志
    log_message('info', '系统初始化完成')
    log_message('error', '这是测试日志error')
    log_message('debug', '这是测试日志debug')

