import logging
import os
import queue
from enum import Enum
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler, QueueHandler, QueueListener
from typing import Dict, Callable, Optional

from config.config import BASE_DIR, get_settings

# 初始化配置
settings = get_settings()
logger = logging.getLogger(settings.app.name)

# 常量定义
LOG_FORMAT = "%(asctime)s - %(module)s - %(funcName)s - line:%(lineno)d - %(levelname)s - %(message)s"
LOG_ACCESS_FILE = os.path.join(BASE_DIR, settings.logging.log_path)
LOG_PATH = os.path.dirname(LOG_ACCESS_FILE)
HANDLER_TYPE = "rotate_file"

# 确保日志目录存在
os.makedirs(LOG_PATH, exist_ok=True)


class LoggerLevel(Enum):
    """日志级别枚举类"""
    DEBUG = ("DEBUG", logging.DEBUG)
    INFO = ("INFO", logging.INFO)
    WARNING = ("WARNING", logging.WARNING)
    ERROR = ("ERROR", logging.ERROR)
    CRITICAL = ("CRITICAL", logging.CRITICAL)

    @property
    def level(self) -> int:
        """获取日志级别数值"""
        return self.value[1]

    @classmethod
    def get_by_config(cls, level_str: str) -> Optional['LoggerLevel']:
        """根据配置字符串获取日志级别枚举"""
        return next((log for log in cls if log.value[0] == level_str), None)


class LoggerFactory:
    """日志工厂类，集中管理日志处理器创建"""

    HANDLERS: Dict[str, Callable] = {
        "default": "_create_default_handler",
        "queue": "_create_queue_handler",
        "rotate_file": "_create_rotate_file_handler",
        "timed_rotate_file": "_create_timed_rotate_file_handler"
    }

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """根据配置获取适当的日志处理器"""
        handler_method = getattr(cls, cls.HANDLERS.get(HANDLER_TYPE, "_create_default_handler"))
        handler = handler_method()
        return cls._setup_logger(handler)

    @classmethod
    def _setup_logger(cls, handler: logging.Handler) -> logging.Logger:
        """配置日志记录器"""
        # 清除现有处理器
        for h in logger.handlers[:]:
            logger.removeHandler(h)
            h.close()

        # 设置日志级别
        logger_level = LoggerLevel.get_by_config(settings.logging.level)
        logger.setLevel(logger_level.level if logger_level else logging.DEBUG)

        # 添加处理器
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)
        return logger

    @classmethod
    def _create_default_handler(cls) -> logging.FileHandler:
        """创建默认文件处理器"""
        print("使用默认文件日志处理器")
        return logging.FileHandler(LOG_ACCESS_FILE, delay=True, encoding="utf-8")

    @classmethod
    def _create_queue_handler(cls) -> QueueHandler:
        """创建队列日志处理器"""
        print("使用异步队列日志处理器")
        log_queue = queue.Queue(-1)  # 无限大小队列
        file_handler = logging.FileHandler(LOG_ACCESS_FILE, delay=True, encoding="utf-8")

        # 创建并启动队列监听器
        listener = QueueListener(
            log_queue,
            file_handler,
            respect_handler_level=True
        )
        listener.start()

        return QueueHandler(log_queue)

    @classmethod
    def _create_rotate_file_handler(cls) -> RotatingFileHandler:
        """创建按文件大小轮转的处理器"""
        print("使用文件大小轮转日志处理器")
        return RotatingFileHandler(
            LOG_ACCESS_FILE,
            maxBytes=settings.logging.rotate_size * 1024 * 1024,
            backupCount=settings.logging.back_files,
            encoding="utf-8"
        )

    @classmethod
    def _create_timed_rotate_file_handler(cls) -> TimedRotatingFileHandler:
        """创建按时间轮转的处理器"""
        print("使用时间轮转日志处理器")
        return TimedRotatingFileHandler(
            LOG_ACCESS_FILE,
            when='midnight',
            interval=1,
            backupCount=settings.logging.back_files,
            encoding="utf-8"
        )


def get_logger() -> logging.Logger:
    """获取配置好的日志记录器"""
    return LoggerFactory.get_logger()