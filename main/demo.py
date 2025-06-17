from datetime import datetime, timezone, timedelta
from logtime import log_message  # 修改导入对象
import time  # 新增导入time模块

if __name__ == '__main__':
    # 输出当前时间
    while True:
        time_str = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] 
        # 输出格式化时间
        log_message('info', f'{time_str}')  # 修改调用方式
        time.sleep(1)  # 新增暂停1秒