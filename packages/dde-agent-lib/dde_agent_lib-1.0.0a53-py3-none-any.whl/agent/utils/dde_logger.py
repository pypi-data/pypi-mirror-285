import logging
import os
import threading
from logging import Logger

from agent.init_env_val import environment
from agent.utils.nacos_val import get_system_config_from_nacos
from nb_log_file_handler import NbLogFileHandler
import asgi_correlation_id
from aliyun.log import QueuedLogHandler, SimpleLogHandler

from agent.config.app_config import get_app_config
from agent.enums.log_type_enum import LogTypeEnum
from agent.enums.task_subtype_enum import TaskSubtypeEnum


class DdeLogger:
    _logger = None
    _lock = threading.Lock()

    @classmethod
    def get_logger(cls) -> Logger:
        if cls._logger is None:
            with cls._lock:
                if cls._logger is None:
                    cls._init_logger()
        return cls._logger

    @classmethod
    def _init_logger(cls):

        if DdeLogger._logger is not None:
            return

        # 创建一个日志记录器，将会同时输出日志到控制台和文件中
        cls._logger = logging.getLogger('dde_logger')

        # 获取配置文件
        app_config = get_app_config()

        # 设置日志级别
        log_level = app_config['logging']['log_level']
        cls._logger.setLevel(log_level)

        # 设置日志不传播
        cls._logger.propagate = False

        # 设置日志文件输出目录
        log_directory = app_config['logging']['log_directory']
        log_file = app_config['logging']['log_file']
        try:
            if not os.path.exists(log_directory):
                os.makedirs(log_directory, exist_ok=True)
        except:
            pass

        # 创建一个处理器，用于写入日志文件
        file_handler = NbLogFileHandler(file_name=log_file, log_path=log_directory, max_bytes=20 * 1000 * 1000,
                                        back_count=10)
        file_handler.setLevel(log_level)

        # 创建一个处理器，用于将日志输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # 创建一个格式器，用于格式化日志条目
        log_format = app_config['logging']['log_format']
        formatter = logging.Formatter(log_format)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 创建一个处理器，用于上报日志到SLS
        log_store = app_config['logging']['log_store']
        system_config = get_system_config_from_nacos()
        sls_handler = QueuedLogHandler(end_point=system_config["sls"]["zhejianglab"]["end_point"],access_key_id=system_config["sls"]["zhejianglab"]["access_key_id"],access_key=system_config["sls"]["zhejianglab"]["access_key"], project=system_config["sls"]["zhejianglab"]["project"], log_store=log_store)
        sls_handler.setLevel(log_level)
        sls_handler.setFormatter(formatter)

        cls._logger.addFilter(asgi_correlation_id.CorrelationIdFilter())

        # 将处理器添加到日志记录器
        cls._logger.addHandler(file_handler)
        cls._logger.addHandler(console_handler)
        cls._logger.addHandler(sls_handler)

        nacos_logger = logging.getLogger('nacos')
        nacos_logger.setLevel(logging.WARNING)


env = environment


def format_log(level=LogTypeEnum.WARNING, _type=None, subtype=TaskSubtypeEnum.DEFAULT.value, environment=env,
               content=None, status=0, errorCode="0", timecost=0, extra=None):
    try:
        kwargs = locals()
        kwargs.pop("level")
        if timecost != 0:
            kwargs["timecost"] = format(timecost, '.6f')
        if level == LogTypeEnum.WARNING:
            fun = dde_logger.warning
        elif level == LogTypeEnum.ERROR:
            kwargs["status"] = 1
            fun = dde_logger.error
        elif level == LogTypeEnum.DEBUG:
            fun = dde_logger.debug
        else:
            fun = dde_logger.info
        log_info = "|".join(map(str, list(kwargs.values())))
        fun(log_info)
    except Exception as e:
        dde_logger.error(f"日志上报发生异常[{str(e)}]异常", exc_info=True)


def get_business_subtype(path: str):
    if path.endswith("document_parsing"):
        return TaskSubtypeEnum.DOCUMENT_PARSING.value
    elif path.endswith("data_visualization"):
        return TaskSubtypeEnum.DATA_VISILIZATION.value
    elif path.endswith("picture2table"):
        return TaskSubtypeEnum.PICTURE_2_TABLE.value
    else:
        return TaskSubtypeEnum.DEFAULT.value

dde_logger = DdeLogger.get_logger()
