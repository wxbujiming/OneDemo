"""
系统日志模块，提供日志记录功能
支持不同级别的日志记录(info/error/warning/debug/critical)
日志会自动保存到指定目录的日期文件中
"""
import logging
import os
import config
from datetime import datetime
import threading
import time

class DateRotatingFileHandler(logging.FileHandler):
    """改进的按日期轮转日志处理器，解决文件创建验证矛盾问题"""
    
    def __init__(self, log_dir=config.logs_path, encoding='utf-8', backup_count=30, check_interval=3600):
        print(log_dir)
        self.log_dir = self._get_absolute_path(log_dir)
        self.backup_count = backup_count
        self.current_date = self._get_current_date()
        self.base_filename = self._get_log_filename()
        self.check_interval = check_interval
        self.encoding = encoding
        
        # 记录当前工作目录用于调试
        self.current_work_dir = os.getcwd()
        self._log_debug(f"当前工作目录: {self.current_work_dir}")
        
        # 验证日志目录
        self._validate_log_directory()
            
        super().__init__(self.base_filename, encoding=encoding)
        self.cleanup_old_logs()
        self._log_debug(f"初始化日志处理器，当前日志文件: {self.base_filename}")
        
        # 启动定时检查线程
        self._start_check_thread()
    
    def _get_absolute_path(self, path):
        """获取路径的绝对路径"""
        abs_path = os.path.abspath(path)
        self._log_debug(f"路径转换: {path} -> {abs_path}")
        return abs_path
        
    def _validate_log_directory(self):
        """验证日志目录是否存在且可写"""
        try:
            if not os.path.exists(self.log_dir):
                self._log_debug(f"日志目录不存在，创建目录: {self.log_dir}")
                os.makedirs(self.log_dir, exist_ok=True)
                
            # 检查目录是否可写
            test_file = os.path.join(self.log_dir, f".write_test_{int(time.time())}.tmp")
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write("test")
            file_exists = os.path.exists(test_file)
            file_size = os.path.getsize(test_file) if file_exists else 0
            os.remove(test_file)
            
            self._log_debug(f"日志目录验证: {self.log_dir}")
            self._log_debug(f"测试文件创建: {'成功' if file_exists else '失败'}")
            self._log_debug(f"测试文件大小: {file_size} bytes")
        except PermissionError:
            self._log_debug(f"权限错误: 无法写入日志目录 {self.log_dir}")
            raise
        except Exception as e:
            self._log_debug(f"日志目录验证失败: {str(e)}")
            raise
            
    def _get_current_date(self):
        """获取当前日期字符串"""
        return datetime.now().strftime('%Y-%m-%d')
        
    def _get_log_filename(self):
        """生成日志文件名，使用绝对路径"""
        filename = f'{self.current_date}.log'
        full_path = os.path.join(self.log_dir, filename)
        abs_path = self._get_absolute_path(full_path)
        return abs_path
        
    def _log_debug(self, message):
        """记录处理器内部调试信息"""
        print(f"[日志处理器调试] {message}")
        
    def _start_check_thread(self):
        """启动定时检查日期变化的线程"""
        def check_date_loop():
            while True:
                time.sleep(self.check_interval)
                current_date = self._get_current_date()
                if current_date != self.current_date:
                    self._log_debug(f"定时检查发现日期变化: {self.current_date} -> {current_date}")
                    self.current_date = current_date
                    threading.Thread(target=self._rotate_log, daemon=True).start()
                    
        self.check_thread = threading.Thread(target=check_date_loop, daemon=True)
        self.check_thread.name = "LogDateChecker"
        self.check_thread.start()
        self._log_debug(f"启动日期检查线程，间隔: {self.check_interval}秒")
        
    def emit(self, record):
        """检查日期是否变化，如果变化则轮转日志文件"""
        current_date = self._get_current_date()
        
        if current_date != self.current_date:
            self._log_debug(f"日志记录时发现日期变化: {self.current_date} -> {current_date}")
            self.current_date = current_date
            self._rotate_log()
            
        super().emit(record)
        
    def _rotate_log(self):
        """执行日志轮转，增加路径调试和重试机制"""
        try:
            self._log_debug(f"开始日志轮转: {self.base_filename}")
            
            # 关闭当前文件流
            if self.stream:
                self._log_debug(f"关闭当前日志文件: {self.base_filename}")
                try:
                    self.stream.flush()
                    self.stream.close()
                    self._log_debug(f"成功关闭当前日志文件")
                except Exception as e:
                    self._log_debug(f"关闭文件失败: {str(e)}")
                finally:
                    self.stream = None
                
            # 更新文件名
            new_filename = self._get_log_filename()
            self._log_debug(f"新日志文件绝对路径: {new_filename}")
            
            # 尝试创建新文件，带重试机制
            max_retries = 3
            retry_count = 0
            file_created = False
            
            while retry_count < max_retries and not file_created:
                try:
                    self._log_debug(f"尝试创建新日志文件 (重试 {retry_count+1}/{max_retries})")
                    # 显式指定绝对路径打开文件
                    self.stream = open(new_filename, 'a', encoding=self.encoding)
                    self.base_filename = new_filename
                    
                    # 立即写入测试数据并刷新
                    test_message = f"=== 日志文件创建于 {datetime.now()} ===\n"
                    self.stream.write(test_message)
                    self.stream.flush()
                    
                    # 验证文件是否真的创建
                    if os.path.exists(new_filename):
                        file_size = os.path.getsize(new_filename)
                        self._log_debug(f"文件创建成功，大小: {file_size} bytes")
                        self._log_debug(f"文件绝对路径: {os.path.abspath(new_filename)}")
                        self._log_debug(f"当前工作目录: {os.getcwd()}")
                        file_created = True
                    else:
                        self._log_debug(f"文件创建后检查失败: 文件不存在")
                        
                except Exception as e:
                    self._log_debug(f"创建新日志文件失败 (重试 {retry_count+1}): {str(e)}")
                    retry_count += 1
                    time.sleep(1)  # 等待1秒后重试
            
            if not file_created:
                self._log_debug(f"所有重试均失败，无法创建新日志文件")
                # 尝试恢复旧文件
                if self.base_filename and os.path.exists(self.base_filename):
                    self.stream = open(self.base_filename, 'a', encoding=self.encoding)
                    self._log_debug(f"恢复写入旧日志文件: {self.base_filename}")
            
            self.cleanup_old_logs()
        except Exception as e:
            self._log_debug(f"日志轮转过程中发生错误: {str(e)}")
            
    def cleanup_old_logs(self):
        """清理超过保留天数的日志文件"""
        if self.backup_count <= 0:
            return
            
        try:
            log_files = []
            for f in os.listdir(self.log_dir):
                if f.endswith('.log') and len(f) == 14:
                    date_str = f[:10]
                    try:
                        datetime.strptime(date_str, '%Y-%m-%d')
                        log_files.append((date_str, f))
                    except ValueError:
                        continue
            
            log_files.sort(reverse=True, key=lambda x: x[0])
            self._log_debug(f"发现{len(log_files)}个日志文件，保留最新{self.backup_count}个")
            
            for date_str, filename in log_files[self.backup_count:]:
                file_path = os.path.join(self.log_dir, filename)
                try:
                    os.remove(file_path)
                    self._log_debug(f"已删除旧日志文件: {filename}")
                except Exception as e:
                    self._log_debug(f"删除旧日志文件失败 {filename}: {str(e)}")
        except Exception as e:
            self._log_debug(f"清理旧日志文件时出错: {str(e)}")

class LogTime:
    """日志输出模块，支持按日期生成日志文件"""
    
    def __init__(self, log_dir=config.logs_path, log_format=None, backup_count=30, check_interval=3600):
        if log_format is None:
            log_format = '%(asctime)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(log_format)
            
        self.logger = logging.getLogger('LogTime')
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers = []  # 清除现有处理器
            
        try:
            file_handler = DateRotatingFileHandler(
                log_dir=log_dir,
                encoding='utf-8',
                backup_count=backup_count,
                check_interval=check_interval
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            self._log_debug("日志模块初始化成功")
        except Exception as e:
            self._log_debug(f"日志模块初始化失败: {str(e)}")
            raise
        
    def _log_debug(self, message):
        print(f"[日志模块调试] {message}")
        
    def debug(self, message):
        self.logger.debug(message)
        
    def info(self, message):
        self.logger.info(message)
        
    def error(self, message):
        self.logger.error(message)

# 示例用法
if __name__ == "__main__":
    # 创建日志实例，设置每60秒检查一次日期变化
    try:
        log = LogTime(check_interval=60)
        
        # 输出不同级别的日志
        log.debug("这是一个debug级别的日志消息")
        log.info("这是一个info级别的日志消息")
        log.error("这是一个error级别的日志消息")
        print("日志模块已更新，增强了文件操作错误处理和调试信息")
    except Exception as e:
        print(f"初始化日志模块失败: {str(e)}")

