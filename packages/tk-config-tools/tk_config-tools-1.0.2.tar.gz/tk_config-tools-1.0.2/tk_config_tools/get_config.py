import os
import json
from utils.date_util import get_second_timestamp
from utils.file_util import get_current_project_name
from tk_config_tools.config_request import http_get_config

local_created_at = 0
cache_config = {}
default_port = "5001"
# default_ip = "192.168.100.1"
default_ip = "127.0.0.1"
default_interval = 60 * 3
default_env = "prod"
default_result_dir = "./"


# 更新本地文件
def get_and_set_local_config(
        result_dir=default_result_dir, key="config", group=get_current_project_name(), env=default_env, ip=default_ip,
        port=default_port, interval=default_interval):
    """
    获取配置信息并缓存到文件中

    Args:
        :param key: 键信息 默认config
        :param group: 组信息 默认获取项目名
        :param env: 环境信息 默认prod
        :param result_dir:默认./
        :param ip: 默认192.168.100.1
        :param port: 默认5001
        :param interval: 默认3小时
    """
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    # 构建文件名
    filename = f"{env}_{group}_{key}.json"
    file_path = os.path.join(result_dir, filename)

    global local_created_at
    global cache_config
    if get_second_timestamp() - local_created_at <= interval:
        if os.path.exists(file_path):
            # 读取缓存文件的数据和生成时间
            with open(file_path, "r") as f:
                data = json.load(f)
                created_at = get_second_timestamp
                cache_config = data["config"]
            if get_second_timestamp() - created_at <= interval:
                return cache_config

    data = http_get_config(ip, port, env, group, key)
    if not data:
        print(f"获取配置信息失败，请检查环境信息、组信息、键信息是否正确")
        return None
    cache_config = data['config']
    # 检查是否有本地文件
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump({"created_at": get_second_timestamp(), "config": cache_config}, f, ensure_ascii=False)
    else:
        with open(filename, "w") as f:
            json.dump({"created_at": get_second_timestamp(), "config": cache_config}, f, ensure_ascii=False)

    # 更新文件生成时间
    local_created_at = get_second_timestamp()
    return cache_config


# 不更新本地文件，只保留缓存
def get_config(key="config", group=get_current_project_name(), env=default_env, ip=default_ip, port=default_port,
               interval=default_interval):
    """
    获取配置信息并缓存到文件中

    Args:
         :param key: 键信息 默认config
        :param group: 组信息 默认获取项目名
        :param env: 环境信息 默认prod
        :param result_dir:默认./
        :param ip: 默认192.168.100.1
        :param port: 默认5001
        :param interval: 默认3小时
    """

    global local_created_at
    global cache_config
    if get_second_timestamp() - local_created_at <= interval and cache_config:
        return cache_config
    data = http_get_config(ip, port, env, group, key)
    if not data:
        print(f"获取配置信息失败，请检查环境信息、组信息、键信息是否正确")
        return None
    cache_config = data['config']
    # 更新文件生成时间
    local_created_at = get_second_timestamp()
    return cache_config


# 不更新本地文件，只保留缓存
def get(key):
    return get_config(key=key)


def get_default():
    return get_config()


def get_and_set_local(key):
    return get_and_set_local_config(key=key)


def get_and_set_local_config_default(key):
    return get_and_set_local_config(key=key)


if __name__ == '__main__':
    print(get_default())
