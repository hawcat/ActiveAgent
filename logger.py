import logging
import os
import sys
import traceback
from logging.handlers import TimedRotatingFileHandler


class hFormatter(logging.Formatter):
    def format(self, record):
        if hasattr(record, "cfilename"):
            record.filename = record.cfilename
        if hasattr(record, "clineno"):
            record.lineno = record.clineno
        return super().format(record)


class hLogger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, name="app", log_dir="logs", log_level=logging.INFO):
        """
        Initialize the logger.
        :param name: logger name
        :param log_dir: log file directory
        :param log_level: logger level
        """
        self.logger = logging.getLogger(name)
        self.logger.propagate = False  # Prevent duplicate output
        self.logger.setLevel(log_level)

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file = os.path.join(log_dir, f"{name}.log")

        # Log file handler
        file_handler = TimedRotatingFileHandler(
            filename=log_file,
            when="midnight",
            interval=1,
            backupCount=30,  # 保留30天的日志文件
            encoding="utf-8",
            delay=False,
            atTime=None,
        )
        file_handler.suffix = "%Y-%m-%d"

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)

        # Logger formatter
        formatter = hFormatter(
            "[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handler
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        sys.excepthook = self.exception_handler

    @classmethod
    def get_logger(cls, name="app", log_dir="logs", log_level=logging.DEBUG):
        """
        获取logger实例的类方法
        :param name: 日志器名称
        :param log_dir: 日志文件存储目录
        :param log_level: 日志级别
        :return: hLogger实例
        """
        if cls._instance is None:
            cls._instance = hLogger(name, log_dir, log_level)
        return cls._instance

    def get_current_frame_info(self):
        """get lineno and filename"""
        try:
            frame = sys._getframe(3)  # 向上获取3层调用栈的帧
            filename = os.path.basename(frame.f_code.co_filename)
            lineno = frame.f_lineno
            return filename, lineno
        except Exception:
            return "unknown", 0

    def _log(self, level, msg, exc_info=None):
        """
        Rewrite the log method to add filename and lineno
        :param level: log level
        :param msg: log info
        :param exc_info: exception info
        """
        filename, lineno = self.get_current_frame_info()
        extra = {"cfilename": filename, "clineno": lineno}
        self.logger.log(level, msg, exc_info=exc_info, extra=extra)

    def debug(self, msg):
        """Record debug level log"""
        self._log(logging.DEBUG, msg)

    def success(self, msg):
        """Record success level log"""
        self._log(logging.INFO, msg)

    def info(self, msg):
        """Record info level log"""
        self._log(logging.INFO, msg)

    def warning(self, msg):
        """Record warning level log"""
        self._log(logging.WARNING, msg)

    def error(self, msg, exc_info=None):
        """
        Record error level log using in try catch
        :param msg: error info
        :param exc_info: trackback info
        """
        self._log(logging.ERROR, msg, exc_info=exc_info)

    def exception(self, msg):
        """Record exception using try catch"""
        self._log(logging.ERROR, msg, exc_info=True)

    def critical(self, msg, exc_info=None):
        """Record critical level log"""
        self._log(logging.CRITICAL, msg, exc_info=exc_info)

    @staticmethod
    def get_traceback():
        """获取当前异常的完整堆栈跟踪信息"""
        return traceback.format_exc()

    def exception_handler(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        self._log(
            logging.CRITICAL,
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback),
        )
