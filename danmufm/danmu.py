#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
弹幕fm主程序
"""

# from threading import Thread
# import subprocess
import logging
import sys
import os
from danmufm.client.douyu_client import DouyuClient
from danmufm.client.ximalaya_client import XimalayaClient

# root logger config
logging.basicConfig(
    format="%(asctime)s - \
[%(process)d]%(filename)s:%(lineno)d - %(levelname)s: %(message)s",
    datefmt='%Y-%m-%d %H:%I:%S',
    filename=os.path.expanduser('~/.doubanfm.log'),
    level=logging.INFO
)

# Set up our own logger
logger = logging.getLogger('danmufm')
logger.setLevel(logging.INFO)

def main():
    if len(sys.argv) > 2:
        print("输入参数大于2,请重新运行命令")
        exit(1)

    url = sys.argv[1]
    # 如果是斗鱼
    if "ximalya.com" in url :
        logger.info("初始喜马拉雅弹幕助手")
        XimalayaClient(url)
    else:
    # 如果是喜马拉雅
        logger.info("初始斗鱼弹幕助手")
        DouyuClient(url)


if __name__ == "__main__":
    main()

