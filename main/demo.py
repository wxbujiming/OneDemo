from datetime import datetime, timezone, timedelta
from logtime import log_message
import time

if __name__ == '__main__':
    # 主程序入口
    # 持续输出当前时间的无限循环
    while True:
        # 获取当前东八区时间并格式化为字符串(精确到毫秒)
        time_str = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] 
        # 调用日志模块记录当前时间(INFO级别)
        log_message('info', f'{time_str}')  
        # 暂停15秒后继续下一次记录
        time.sleep(15)