import socket

import requests


# # 调用函数获取内网 IP
# ip = get_internal_ip()
# print(ip)


def http_get_config(ip, port, env, group, key):
    url = f"http://{ip}:{port}/get_config?group={group}&key={key}&env={env}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['statusCode'] == 200:
            return data['data']
        else:
            print(f"Failed to get config. Status code: {data['statusCode']}, Message: {data['statusMessage']}")
    else:
        print(f"Failed to send request. Status code: {response.status_code}")

    return None


def http_add_config(ip, port, env, group, key, config):
    print(ip, port, env, group, key, config)
    url = f"http://{ip}:{port}/add_config"

    data = {
        'env': env,
        'group': group,
        'key': key,
        'config': config
    }

    response = requests.post(url, json=data)
    if response.status_code == 200:
        data = response.json()
        if data['statusCode'] == 200:
            print("Config added successfully.")
        else:
            print(f"Failed to add config. Status code: {data['statusCode']}, Message: {data['statusMessage']}")
    else:
        print(f"Failed to send request. Status code: {response.status_code}")


def get_internal_ip():
    try:
        # 创建一个 UDP 套接字
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # 连接到一个外部的 IP 地址（此处选择了 Google 的 DNS 服务器）
        sock.connect(('8.8.8.8', 80))

        # 获取套接字绑定的本地地址信息
        internal_ip = sock.getsockname()[0]

        return internal_ip
    except socket.error:
        return None
