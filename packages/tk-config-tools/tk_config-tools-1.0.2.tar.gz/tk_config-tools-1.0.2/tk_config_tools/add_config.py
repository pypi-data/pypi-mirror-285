import json

import account_config
from config_request import http_add_config
from get_config import default_ip, default_port, get_current_project_name, default_env


def upload_local_json_config(file_path, key="config", ip=default_ip, port=default_port, env=default_env,
                             group=get_current_project_name()):
    with open(file_path, 'r') as file:
        json_data = json.load(file)
    http_add_config(ip, port, env, group, key, json_data)


def upload_local_dict_config(dictionary, key="config", ip=default_ip, port=default_port, env=default_env,
                             group=get_current_project_name()):
    http_add_config(ip, port, env, group, key, dictionary)


def upload_local_json_config_by_default(file_path):
    upload_local_json_config(file_path=file_path)


def upload_local_dict_config_by_default(key, dictionary):
    upload_local_dict_config(dictionary=dictionary, key=key)


if __name__ == '__main__':
    pass
    # print(get_dict_file_name(account_config.accounts))
    # print(get_variable_name(account_config.accounts))
    # print(get_current_project_name())
    # print(get_file_name_without_extension("/Users/zhangjianqiang/PycharmProjects/spider/config/config.json"))

    # 示例用法
    # env = "dev"
    # group = "spider"
    # key = "server_url"
    # print(upload_local_dict_config("127.0.0.1", 5001, env, group, key, account_config.accounts))
    print(upload_local_json_config_by_default("/Users/zhangjianqiang/PycharmProjects/spider/config/config.json"))
