#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
弹幕fm主程序
"""
import argparse
import gettext
import psycopg2
import io
import json
import logging
import os
import re
import sys
import time
from .settings import ROOT_PROJECT_DIR , ENGINE
from sqlalchemy.orm import sessionmaker, scoped_session
from .cmd_config import config
# from threading import Thread
# import subprocess
from .client.douyu_client import DouyuClient
from sqlalchemy.util.queue import Empty
import sqlalchemy
import traceback

APP_DESC = """
    _____                                ______ __  __
    |  __ \                              |  ____|  \/  |
    | |  | | __ _ _ __  _ __ ___  _   _  | |__  | \  / |
    | |  | |/ _` | '_ \| '_ ` _ \| | | | |  __| | |\/| |
    | |__| | (_| | | | | | | | | | |_| |_| |    | |  | |
    |_____/ \__,_|_| |_|_| |_| |_|\__,_(_)_|    |_|  |_|

                        ---- A Terminal Tools For DouyuTV

    @author Micheal Gardner (twocucao@gmail.com)
                                    last_update 2016-06-09
"""

logger = logging.getLogger('danmu.fm')


def check_setting_and_env():
    logger.info("程序正在启动,检查环境配置")
    if sys.version_info < (3,2):
        raise RuntimeError("at least Python 3.3 is required!!")
    Session = scoped_session(sessionmaker(bind=ENGINE))
    s = Session()
    try:
        rs_version = s.execute("SELECT VERSION();")
        version = rs_version.fetchone()[0]
        env_infomation = """\
        ------------------------------------------------------------
        PostgreSQL 版本信息 : {0}
        ------------------------------------------------------------
        """.format(version)
        print(env_infomation)
        Session.remove()
    except sqlalchemy.exc.OperationalError as e:
        logger.error("没有初始化数据库")
        # 貌似没什么作用?
        try:
            conn = ENGINE.connect()
            conn.execute("commit")
            conn.execute("create database danmufm")
            conn.close()
        except sqlalchemy.exc.OperationalError as e:
            logger.error("无法创建数据库,请检查配置")
            logger.info("程序退出")
            exit()
        pass

    logger.info("开始配置环境")

import click

@click.command()
@click.argument('url', required=True)
@click.option('-q','--quality', default=0, help='查看视频清晰度, 0: 无, 1:流畅, 2:普通, 3:高清,')
@click.option('-m','--mode', default=0 , help='选择弹幕类型,0为默认普通弹幕,1为海量弹幕')
@click.option('-p','--path', default=".",type=click.Path(), help='视频缓存本地地址,注:quality必须要为1-2-3其中之一')
@click.option('-v','--verbose', count=True, help='-v 为普通日志模式, -vvvv 超级海量日志模式')
def parse_command(quality, mode , path , verbose , url):
    """
指定获取主播的房间地址对主播直播情况进行抓取与统计 (Mac and Ubuntu Only)

Example:

    danmu.fm -q 2 -v 1 http://www.douyu.com/qiuri

    danmu.fm -q 3 -m 0 -p "videos/20160609_1900_2240_小苍.mp4" -v 1 http://www.douyu.com/qiuri

    """

    # danmu.fm -q 3 -m 0 -p "videos/20160609_1900_2240_小苍.mp4"-v 1 http://www.douyu.com/qiuri
    config["video_quality"] = quality if quality <= -1  or quality >= 3 else 0
    config["danmu_mode"] = mode if mode <= -1 or mode >= 2 else 0
    config["video_stored_path"] = path
    config["verbose"] = verbose
    config["zhubo_room_url"] = url
    logging.info("正在检查环境")
    check_setting_and_env()
    logging.info("环境检查完毕,正在开启斗鱼客户端")
    start_douyu_client()

def start_douyu_client():
    print("---------")
    url     = config["zhubo_room_url"]
    DouyuClient(url,config)

def main():
    print(APP_DESC)
    parse_command()



if __name__ == "__main__":
    main()

