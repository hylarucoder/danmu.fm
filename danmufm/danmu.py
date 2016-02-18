#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
弹幕fm主程序
"""
import logging
import argparse
import gettext
import io
import json
import os
import sys
import time

# from threading import Thread
# import subprocess
from .client.douyu_client import DouyuClient

if sys.version_info < (3,):
    raise RuntimeError("at least Python3.0 is required!!")
APP_DESC = """

 _____                                ______ __  __
|  __ \                              |  ____|  \/  |
| |  | | __ _ _ __  _ __ ___  _   _  | |__  | \  / |
| |  | |/ _` | '_ \| '_ ` _ \| | | | |  __| | |\/| |
| |__| | (_| | | | | | | | | | |_| |_| |    | |  | |
|_____/ \__,_|_| |_|_| |_| |_|\__,_(_)_|    |_|  |_|

                    ---- A Terminal Tools For DouyuTV

@author Micheal Gardner (twocucao@gmail.com)
                                last_update 2016-02-16
"""


logging.basicConfig(
    format="%(asctime)s - \
[%(process)d]%(filename)s:%(lineno)d - %(levelname)s: %(message)s",
    datefmt='%Y-%m-%d %H:%I:%S',
    # filename=os.path.expanduser('~/.danmu.fm.log'),
    level=logging.INFO
)

logger = logging.getLogger('danmu.fm')

def main():

    print(APP_DESC)
    if len(sys.argv) == 1:
        sys.argv.append('--help')
    parser = argparse.ArgumentParser()
    parser.add_argument('-q','--quality',type=int,help="download video quality : 1 for the standard-definition; 3 for the super-definition")
    parser.add_argument('-v','--verbose', help="print more debuging information")
    parser.add_argument('-s','--store', help="保存流媒体文件到指定位置")
    parser.add_argument('-d','--danmu', help="读取~/.danmu.fm配置,请~/.danmu.fm指定数据库")
    parser.add_argument('url',metavar='URL',nargs='+', help="zhubo page URL (http://www.douyutv.com/*/)")
    args = parser.parse_args()

    #初始化日志
    # logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    logger.setLevel(logging.INFO)
    #视频质量控制
    #0为不下载视频
    #1为普清
    #2为高清
    #3为超清
    qualities = ["","普清","高清","超清"]
    quality = args.quality if args.quality is not None else 0
    if quality < 1 or quality > 3:
        logger.info("解析所有视频流地址")
    else:
        logger.info("解析"+qualities[quality]+"视频地址,并尝试使用Mplayer播放")
    store = args.store if args.store is None else False
    #url
    url = (args.url)[0]
    g_config = {}
    g_config["quality"] = quality
    g_config["store"] = store

    # 如果是斗鱼
    logging.info("初始斗鱼弹幕助手")
    DouyuClient(url,g_config)


if __name__ == "__main__":
    main()

