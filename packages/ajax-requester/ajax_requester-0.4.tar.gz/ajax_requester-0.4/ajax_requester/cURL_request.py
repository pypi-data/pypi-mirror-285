import requests


def curl_to_requests(curl_command):
    """
    将 cURL 命令转换为 Python requests 代码
    :param curl_command: str, cURL 命令
    :return: None
    """
    import shlex

    # 分析 cURL 命令
    tokens = shlex.split(curl_command)

    # 初始化请求数据
    method = None
    url = None
    headers = {}
    data = None

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == 'curl':
            i += 1
            continue
        elif token.startswith('http'):
            url = token
            i += 1
            continue
        elif token == '-X':
            method = tokens[i + 1].upper()
            i += 2
            continue
        elif token.startswith('-H'):
            header = tokens[i + 1]
            key, value = header.split(': ', 1)
            headers[key] = value
            i += 2
            continue
        elif token == '--data-raw' or token == '--data':
            data = tokens[i + 1]
            i += 2
            continue
        else:
            i += 1

    # 如果没有设置方法，默认使用 POST
    if method is None:
        method = 'POST'

    # 打印转换后的 requests 代码
    print("import requests\n")

    if data:
        print(f"data = {data}\n")
    else:
        print("data = None\n")

    print(f"headers = {headers}\n")
    print(f"url = '{url}'\n")

    if method == 'POST':
        print("response = requests.post(url, headers=headers, data=data)")
    else:
        print("response = requests.get(url, headers=headers, params=data)")

    print("print(response.text)")



