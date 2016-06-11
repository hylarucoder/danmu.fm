from subprocess import check_output
from urllib.parse import unquote
from urllib.request import urlopen
import hashlib
import json
import logging
import os
import re
import requests
import subprocess
import threading
import time

from ..cmd_config import room_status, config
from ..settings import CURRENT_USER_HOME_DIR
from .douyu_danmu_manager import DouyuDanmuManager
from danmufm.misc.player import MPlayer

logger = logging.getLogger("danmu.fm")


def valid_json(my_json):
    """ 验证是否为 json 数据格式"""
    try:
        json_object = json.loads(my_json)
    except ValueError as e:
        print(e)
        return False
    return json_object


class DouyuClient(object):
    """
    [TODO:如下]
    1. 初始化Client相关配置(获取)
    2. 获取 房间信息 / 主播信息
    3. 使用DanmuManager获取弹幕信息
    4. 使用队列进行缓存和入库
    """

    def __init__(self, url):
        self.DOUYU_PREFIX = "http://www.douyu.com/"
        if self.DOUYU_PREFIX not in url:
            url = self.DOUYU_PREFIX + url
        self.url = url
        self.mplayer = MPlayer()


    def start(self):
        # 获取房间信息
        auth_server_ip, auth_server_port = self.fetch_room_info(self.url)
        if auth_server_ip == False or auth_server_port == True:
            exit()
        # 获取视频流信息
        self.fetch_rtmp_info()
        # 使用弹幕Manager不断获取弹幕到队列中,并打印出来
        self.fetch_danmu(auth_server_ip,auth_server_port)
        pass

    def fetch_room_info(self, url):

        html = urlopen(url).read().decode()
        room_info_json = re.search('var\s\$ROOM\s=\s({.*});', html).group(1)
        # print(room_info_json)
        auth_server_json = re.search('\$ROOM\.args\s=\s({.*});', html).group(1)
        # print(auth_server_json)
        room_info_json_format = valid_json(room_info_json)
        auth_server_json_format = valid_json(auth_server_json)

        if room_info_json_format != False and auth_server_json_format != False:
            js = room_info_json_format
            room = room_status
            room["id"] = js["room_id"]
            room["name"] = js["room_name"]
            room["gg_show"] = js["room_gg"]["show"]
            room["owner_uid"] = js["owner_uid"]
            room["owner_name"] = js["owner_name"]
            room["room_url"] = js["room_url"]
            room["near_show_time"] = js["near_show_time"]
            room["tags"] = []
            room_tags_json = js["all_tag_list"]
            if js["room_tag_list"] != None:
                room_tags_size = len(js["room_tag_list"])
                for i in range(0, room_tags_size):
                    room["tags"].append(room_tags_json[js["room_tag_list"][i]]["name"])

            auth_servers = valid_json(unquote(auth_server_json_format["server_config"]))
            auth_server_ip = auth_servers[0]["ip"]
            auth_server_port = auth_servers[0]["port"]
            return auth_server_ip, auth_server_port

        else:
            logger.info("请求网页错误,正在退出...")
            return False, False

    def fetch_rtmp_info(self):
        api_url_prefix = "http://douyutv.com/api/v1/"
        cctime = int(time.time())
        md5url = "room/" + str(room_status["id"]) + "?aid=android&client_sys=android&time=" + str(cctime)
        m2 = hashlib.md5(bytes(md5url + "1231", "utf-8"))
        url_json = api_url_prefix + md5url + "&auth=" + m2.hexdigest()
        res = requests.get(url_json)
        js_data = json.loads(res.text)
        # print(js_data)
        # 如果在线,则存在RTMP视频流,否则主播不在线
        if str(js_data["data"]["rtmp_live"]).strip() == "":
            logger.error("当前主播不在线,请切换别的房间试试")
            exit()
        else:
            logger.info("当前主播在线")
        sd_rmtp_url = str(js_data["data"]["rtmp_url"]) + "/" + str(js_data["data"]["rtmp_live"])
        hd_rmtp_url = str(js_data["data"]["rtmp_url"]) + "/" + str(js_data["data"]["rtmp_live"])
        spd_rmtp_url = str(js_data["data"]["rtmp_url"]) + "/" + str(js_data["data"]["rtmp_live"])
        sd_flv_addr = requests.get(sd_rmtp_url, allow_redirects=False).headers["Location"]
        hd_flv_addr = requests.get(hd_rmtp_url, allow_redirects=False).headers["Location"]
        spd_flv_addr = requests.get(spd_rmtp_url, allow_redirects=False).headers["Location"]
        if config["video_stored_path"] != os.getcwd():
            if config["video_quality"] <= 0:
                logger.info("不播放视频")
            elif config["video_quality"] == 1:
                logger.info("正在尝试使用Mplayer播放普清视频" + sd_flv_addr)
                self.mplayer.start(sd_flv_addr)
            elif config["video_quality"] == 2:
                logger.info("正在尝试使用Mplayer播放高清视频" + hd_flv_addr)
                self.mplayer.start(hd_flv_addr)
            else:
                logger.info("正在尝试使用Mplayer播放超清视频" + spd_flv_addr)
                self.mplayer.start(spd_flv_addr)
        else:
            t = threading.Thread(target=self.wget_to_path,args=(config["video_stored_path"],spd_flv_addr,))
            t.setDaemon(True)
            t.start()
        pass
    def wget_to_path(self,path,url):
        cmd = ["/usr/local/bin/wget",
                url,
               "-O",
                os.path.join(path,room_status["owner_name"] + "_" + room_status["name"].strip().replace(" ","_") + str(time.strftime("_%Y%m%d_%H%M%S") + str(".flv")))
               ]
        logger.debug(cmd)
        try:
            check_output(cmd, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(e.output)

        pass





    def fetch_danmu(self, auth_server_ip, auth_server_port):
        client = DouyuDanmuManager(auth_server_ip, auth_server_port)
        client.start()

    def print_room_info(self):
        print("=========================================")
        print("= Room Infomation                       =")
        print("=========================================")
        print("= 房间: " + room_status["name"] + "(" + room_status["id"] + ")")
        print("= 主播: " + room_status["owner_name"] + str(room_status["owner_uid"]))
        print("= 公告: " + re.sub("\n+", "\n", re.sub('<[^<]+?>', '', room_status["gg_show"])))
        print("= 标签: " + str(room_status["tags"]))
        print("= 在线: " + room_status["live_stat"])
        print("= 粉丝: " + room_status["fans_count"])
        print("= 财产: " + room_status["weight"])
        print("=========================================")
