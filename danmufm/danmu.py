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
from client.douyu_client import DouyuClient

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
    logger.info("初始斗鱼弹幕助手")
    DouyuClient(sys.argv[1])


if __name__ == "__main__":
    main()

