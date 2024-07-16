import argparse
import logging
import os

import requests
import yaml

from spacedork import reps, VERSION

logger = logging.getLogger("dork")
formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)
home_directory = os.path.expanduser("~")
config_file_path = os.path.join(home_directory, ".config", 'spacedork', 'config.yaml')


def cmd_parser():
    parser = argparse.ArgumentParser(description='这是一个示例命令行参数解析程序')
    parser.add_argument('--list-module', required=False, help='列举所有模块', action='store_true')
    parser.add_argument('--config', '-c', required=False, help=f'配置文件路径({config_file_path})',
                        default=config_file_path)
    parser.add_argument('--dork', '-q', required=False, help='查询dork关键字')
    parser.add_argument('-x', dest='proxy', required=False, help='配置代理(socks5://127.0.0.1:7890)')
    parser.add_argument('--module', '-m', required=False, default='zoomeye', help='使用查询模型')
    parser.add_argument('--start-page', type=int, default=1, help='要处理的数量')
    parser.add_argument('--end-page', type=int, default=1, help='要处理的数量')
    parser.add_argument('--timeout', '-t', type=int, default=10, help='超时时间(s) 默认10')
    parser.add_argument('--fields', '-f', default="url", help='输出字段(url|ip|port|address)')
    parser.add_argument('-o', dest="output", default="", help='保存为文件')
    parser.add_argument('-v', dest="version", default=False, action='store_true', help='Version')
    parser.add_argument('-debug', default=False, action='store_true', help='DEBUG')
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    if args.version:
        print(VERSION)
        exit()
    if args.fields not in ("url", "ip", "port", "address"):
        print("请选择输出字段(url|ip|port)")
        exit()
    if args.list_module:
        for k, v in reps.repo.items():
            print(k)
        exit()
    elif not args.dork:
        print("请提供dork关键字")
        exit()
    if not os.path.exists(args.config):
        print("配置文件不存在:{}".format(args.config))
        exit()
    return args


def warp_timeout(func, timeout=5):
    def wrapper(*args, **kwargs):
        # 设置超时时间为 5 秒
        if "timeout" not in kwargs:
            kwargs.setdefault('timeout', timeout)
        return func(*args, **kwargs)

    return wrapper


def main():
    args = cmd_parser()
    with open(args.config, "r") as yaml_file:
        try:
            yaml_data = yaml.safe_load(yaml_file)
        except yaml.YAMLError as e:
            logger.error(f"YAML解析错误: {e}")
            return
    plugin = reps.repo.get(args.module)
    plugin_options = yaml_data.get(args.module, {})
    client = requests.Session()
    client.send = warp_timeout(client.send, timeout=args.timeout)
    if args.proxy:
        client.proxies = {"https": args.proxy}
    cls = plugin(client, **plugin_options, fields=args.fields)
    if args.output:
        with open(args.output, 'w') as f:
            for x in cls.query(args.dork, start_page=args.start_page, end_page=args.end_page):
                f.write(x[args.fields] + "\n")
    else:
        for i in cls.query(args.dork, start_page=args.start_page, end_page=args.end_page):
            print(i[args.fields])
    logger.info("Search DONE")


if __name__ == '__main__':
    main()
