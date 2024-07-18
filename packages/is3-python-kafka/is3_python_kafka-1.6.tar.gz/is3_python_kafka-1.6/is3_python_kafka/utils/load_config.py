import configparser
import os


def load_config(configPath):
    config_path = os.path.join(configPath)

    # 确认文件存在
    if os.path.exists(config_path):
        print(f"Config file exists at: {config_path}")
    else:
        print(f"Config file does not exist at: {config_path}")
        exit(1)

    # 读取配置文件
    config = configparser.ConfigParser()
    config.read(config_path)

    return config
