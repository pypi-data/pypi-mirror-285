# coding = utf-8
import logging

def setup_logging():
    #  创建根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # 错误日志写入error.log 文件
    error_handler = logging.FileHandler('error.log')
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    error_handler.setFormatter(error_formatter)

    # 错误日志 写入operation.log 文件
    operation_handler = logging.FileHandler('operation.log')
    operation_handler.setLevel(logging.INFO)
    operation_formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    operation_handler.setFormatter(operation_formatter)

    root_logger.addHandler(error_handler)
    root_logger.addHandler(operation_handler)

# 初始化日志配置
setup_logging()

logger = logging.getLogger(__name__)