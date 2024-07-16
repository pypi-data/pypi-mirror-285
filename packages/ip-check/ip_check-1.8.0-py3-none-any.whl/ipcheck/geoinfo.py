#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from ipcheck import GEO2CITY_DB_NAME, GEO2ASN_DB_NAME, GEO2CITY_DB_PATH, GEO2ASN_DB_PATH, GEO_CONFIG_PATH, GEO_DEFAULT_CONFIG
from ipcheck.app.config import Config
from ipcheck.app.gen_ip_utils import gen_ip_list
from ipcheck.app.geo_utils import check_or_gen_def_config, download_geo_db, parse_geo_config
import argparse
import subprocess
import sys

def get_info():
    parser = argparse.ArgumentParser(description='geo-info 获取ip(s) 的归属地信息')
    parser.add_argument("sources", nargs="+", help="待获取归属地信息的ip(s)")
    args = parser.parse_args()
    config = Config()
    config.skip_all_filters = True
    config.ip_source = args.sources
    ip_list = gen_ip_list(False)
    if ip_list:
        for ip_info in ip_list:
            print(ip_info.geo_info_str)
    else:
        print('请检查是否输入了有效ip(s)')


def download_db():
    parser = argparse.ArgumentParser(description='igeo-dl 升级/下载geo 数据库')
    parser.add_argument("-u", "--url", type=str, default=None, help="geo 数据库下载地址, 要求结尾包含GeoLite2-City.mmdb 或GeoLite2-ASN.mmdb")
    parser.add_argument("-p", "--proxy", type=str, default=None, help="下载时使用的代理")
    args = parser.parse_args()
    url = args.url
    proxy = args.proxy
    if not args.url:
        return self_update(proxy)
    path = None
    if url.endswith(GEO2CITY_DB_NAME):
        path = GEO2CITY_DB_PATH
    if url.endswith(GEO2ASN_DB_NAME):
        path = GEO2ASN_DB_PATH
    if path:
        download_geo_db(url, path, proxy)
    else:
        print('请输入包含{} 或 {} 的url'.format(GEO2CITY_DB_NAME, GEO2ASN_DB_NAME))



def config_edit():
    parser = argparse.ArgumentParser(description='geo-cfg 编辑geo config')
    parser.add_argument("-e", "--example", action="store_true", default=False, help="显示配置文件示例")
    args = parser.parse_args()
    if args.example:
        print(GEO_DEFAULT_CONFIG)
        return
    check_or_gen_def_config()
    print('编辑配置文件 {}'.format(GEO_CONFIG_PATH))
    platform = sys.platform
    if platform.startswith('win'):
        subprocess.run(['notepad.exe', GEO_CONFIG_PATH])
    elif platform.startswith('linux'):
        subprocess.run(['vim', GEO_CONFIG_PATH])
    else:
        print('未知的操作系统，请尝试手动修改{}!'.format(GEO_CONFIG_PATH))


def self_update(proxy=None):
    check_or_gen_def_config()
    db_asn_url, db_city_url, cfg_proxy = parse_geo_config()
    proxy = proxy if proxy else cfg_proxy
    print('ASN 数据库下载地址:', db_asn_url)
    download_geo_db(db_asn_url, GEO2ASN_DB_PATH, proxy)
    print('CITY 数据库下载地址:', db_city_url)
    download_geo_db(db_city_url, GEO2CITY_DB_PATH, proxy)


if __name__ == '__main__':
    get_info()