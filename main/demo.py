import time
from logtime import logger  

if __name__ == '__main__':
    # 输出当前时间
    while True:
        start = time.time()
        # 格式化为年月日时分秒
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start))  # 修改为本地时间
        # 输出格式化时间
        logger.log_message('info', f'Current time: {time_str}')  
        elapsed = time.time() - start  # 计算已用时间
        time.sleep(max(0, 1 - elapsed))  # 确保总间隔1秒