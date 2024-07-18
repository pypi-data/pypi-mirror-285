import logging
import os


def Logging():
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 配置日志记录器
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',  # 设置日志格式
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'info.log'), encoding='utf-8'),  # 设置编码格式为 UTF-8
            logging.StreamHandler()  # 将日志输出到控制台
        ]
    )
