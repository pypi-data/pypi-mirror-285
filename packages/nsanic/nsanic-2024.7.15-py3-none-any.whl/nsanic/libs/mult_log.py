import logging
import os
from logging import handlers


class MultLogger:
    __LOG_OBJ = {}

    def __init__(self, base_path: str = None, folder: str = None):
        self.__path = base_path or os.path.join(os.getcwd(), 'logs')
        self.__folder = folder or 'file_log'

    @staticmethod
    def __create_log_obj(log_path: str, log_name="runs", log_fmt=None) -> logging:
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        if not log_fmt:
            log_fmt = "%(asctime)s - %(process)d:%(lineno)s:%(levelname)s - %(message)s"
        log_item = logging.getLogger(f"{log_path}_{log_name}")
        if log_item.handlers:
            return log_item
        formatter = logging.Formatter(fmt=log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        log_handler = handlers.RotatingFileHandler(
            filename=os.path.join(log_path, f"{log_name}.log"), mode="a", maxBytes=52428800,
            backupCount=10, encoding='utf-8')
        log_item.setLevel(logging.INFO)
        log_handler.setFormatter(formatter)
        log_item.addHandler(log_handler)
        return log_item

    def base_log_obj(self, file_name="runs", folder=None, log_fmt=None):
        """
        添加日志

        :param file_name: 日志文件名 默认为‘run_info’（多字段命名请用下划线连接 不能带空格）
        :param folder: 日志目录名 默认无目录 既是项目日志目录下的子目录名 不建议使用更多级的目录
        :param log_fmt: 日志记录格式 默认为 ‘%(asctime)s - %(process)d:%(lineno)s:%(levelname)s - %(message)s’ 格式
        """
        path = os.path.join(self.__path, self.__folder)
        pathname = os.path.join(path, file_name) if not folder else os.path.join(os.path.join(path, folder), file_name)
        obj = self.__LOG_OBJ.get(pathname)
        if obj:
            return obj
        obj = self.__create_log_obj(log_path=path, log_name=file_name, log_fmt=log_fmt)
        self.__LOG_OBJ[pathname] = obj
        return obj

    def error(self, *out_info):
        """代码或执行失败或报错的日志"""
        obj = self.base_log_obj(file_name='failed')
        obj.error(str(out_info[0]) if len(out_info) == 1 else str(out_info))

    def info(self, *out_info):
        """标记或打印类的日志"""
        obj = self.base_log_obj(file_name='info')
        obj.info(str(out_info[0]) if len(out_info) == 1 else str(out_info))
