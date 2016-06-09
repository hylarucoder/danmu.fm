import datetime
import re
import uuid
import hashlib
import socket
import requests
import json
import threading
import time
from ..misc.player import MPlayer
from ..misc.color_printer import ColorPrinter
from ..model.douyu_msg import DouyuMsg
# import sys
import logging

logger = logging.getLogger("danmufm")
class DouyuDanmuClient(object):

    """Docstring for DouyuDanmuClient. """

    def __init__(self,room,auth_dst_ip,auth_dst_port,g_config):
        self.DANMU_ADDR = ("danmu.douyutv.com",8602)
        self.g_config = g_config
        self.DANMU_AUTH_ADDR = (auth_dst_ip,int(auth_dst_port))
        self.room = room
        self.room_id = str(room["id"])
        self.auth_dst_ip = auth_dst_ip
        self.auth_dst_port = auth_dst_port
        self.dev_id = str(uuid.uuid4()).replace("-","")
        self.mplayer = MPlayer()


    def start(self):
        self.do_login()
        if self.live_stat == "离线":
            logger.info("主播离线中,正在退出...")
        else:
            logger.info("主播在线中,准备获取弹幕...")
            self.print_room_info()
            t = threading.Thread(target=self.keeplive)
            t.setDaemon(True)
            t.start()
            while True:
                self.get_danmu()

    def print_room_info(self):
        api_url_prefix = "http://douyutv.com/api/v1/"
        cctime = int(time.time())
        md5url = "room/" + str(self.room_id) + "?aid=android&client_sys=android&time=" + str(cctime)
        m2 = hashlib.md5(bytes(md5url + "1231","utf-8"))
        self.url_json = api_url_prefix + md5url + "&auth=" + m2.hexdigest()
        res = requests.get(self.url_json)
        js_data = json.loads(res.text)

        sd_rmtp_url = str(js_data["data"]["rtmp_url"]) + "/" + str(js_data["data"]["rtmp_live"])
        hd_rmtp_url = str(js_data["data"]["rtmp_url"]) + "/" +str(js_data["data"]["rtmp_live"])
        spd_rmtp_url = str(js_data["data"]["rtmp_url"]) + "/" +str(js_data["data"]["rtmp_live"])
        sd_flv_addr = requests.get(sd_rmtp_url,allow_redirects=False).headers["Location"]
        hd_flv_addr = requests.get(hd_rmtp_url,allow_redirects=False).headers["Location"]
        spd_flv_addr = requests.get(spd_rmtp_url,allow_redirects=False).headers["Location"]
        if self.g_config["quality"] <= 0 or self.g_config["quality"] >= 4:
            logger.info("不播放视频")
        elif self.g_config["quality"] == 1:
            logger.info("正在尝试使用Mplayer播放普清视频" + sd_flv_addr)
            self.mplayer.start(sd_flv_addr)
        elif self.g_config["quality"] == 2:
            logger.info("正在尝试使用Mplayer播放高清视频" + hd_flv_addr)
            self.mplayer.start(hd_flv_addr)
        else:
            logger.info("正在尝试使用Mplayer播放超清视频" + spd_flv_addr)
            self.mplayer.start(spd_flv_addr)
        print( "=========================================")
        print( "= Room Infomation                       =")
        print( "=========================================")
        print( "= 房间: "+self.room["name"]+"("+self.room_id +")")
        print( "= 主播: "+self.room["owner_name"]+str(self.room["owner_uid"]))
        print( "= 公告: "+re.sub("\n+","\n",re.sub('<[^<]+?>', '', self.room["gg_show"])))
        print( "= 标签: "+str(self.room["tags"]))
        print( "= 在线: "+self.live_stat)
        print( "= 粉丝: "+self.fans_count)
        print( "= 财产: "+self.weight)
        print( "=========================================")

    def keeplive(self):
        print("启动 KeepLive 线程")
        while True:
            self.send_auth_keeplive_msg()
            self.send_danmu_keeplive_msg()
            time.sleep(40)


    def do_login(self):
        self.danmu_auth_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.danmu_auth_socket.connect(self.DANMU_AUTH_ADDR)
        self.danmu_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.danmu_socket.connect(self.DANMU_ADDR)
        self.send_auth_loginreq_msg()
        recv_msg = self.auth_recv()
        print(recv_msg)
        if "live_stat@=0" in recv_msg:
            self.live_stat = "离线"
        else:
            self.live_stat = "在线"
            self.username = re.search('\/username@=(.+)\/nickname', recv_msg).group(1)
            recv_msg = self.auth_recv()
            # self.gid = re.search('\/gid@=(\d+)\/', recv_msg).group(1) # 取消注释可以直接使用正常方式
            self.gid = '-9999' # 据说 9999 可以直接获取海量字幕,以后有机会增加命令行配置
            self.weight = re.search('\/weight@=(\d+)\/', recv_msg).group(1)
            self.fans_count = re.search('\/fans_count@=(\d+)\/', recv_msg).group(1)
            self.send_qrl_msg()
            recv_msg = self.auth_recv()
            # print(recv_msg)
            # recv_msg = self.auth_recv()
            # print(recv_msg)
            self.send_auth_keeplive_msg()
            recv_msg = self.auth_recv()
            # print(recv_msg)
            self.send_danmu_loginreq_msg()
            recv_msg = self.danmu_recv()
            # print(recv_msg)
            self.send_danmu_join_group_msg()


    def get_danmu(self):
        recv_msg = self.danmu_recv()
        if "type@=" not in recv_msg:
            print(recv_msg)
            print("无效消息")
        elif "type@=error" in recv_msg:
            print("错误消息,可能认证失效")
        else:
            msg_content = recv_msg.replace("@S","/").replace("@A=",":").replace("@=",":")
            # print(msg_content)
            try:
                msg_type = re.search('type:(.+?)\/', msg_content).group(1)

                if msg_type == "chatmsg":
                    msg_type_zh = "弹幕消息"
                    sender_id = re.search('\/uid:(.+?)\/', msg_content).group(1) if 'uid:' in msg_content else "unknown"
                    nickname = re.search('\/nn:(.+?)\/', msg_content).group(1) if 'nn:' in msg_content else "unknown"
                    content = re.search('\/txt:(.+?)\/', msg_content).group(1) if 'txt:' in msg_content else "unknown"
                    level = re.search('\/level:(.+?)\/', msg_content).group(1) if 'level:' in msg_content else "unknown"
                    client_type = re.search('\/ct:(.+?)\/', msg_content).group(1)  if 'ct:' in msg_content else "unknown"# ct 默认值 0 web
                    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ColorPrinter.green("|" + msg_type_zh + "| " + self.align_left_str(nickname,20," ") + self.align_left_str("<Lv:" + level + ">",8," ") + self.align_left_str("("+ sender_id +")",13," ") + self.align_left_str("["+client_type+"]",10," ") + "@ "+time+": " + content +" ")

                elif msg_type == "uenter":
                    msg_type_zh = "入房消息"
                    user_id = re.search('\/uid:(.+?)\/', msg_content).group(1) if 'uid:' in msg_content else "unknown"
                    nickname = re.search('\/nn:(.+?)\/',msg_content).group(1) if 'nn:' in msg_content else "unknown"
                    strength = re.search('\/str:(.+?)\/',msg_content).group(1) if 'str:' in msg_content else "unknown"
                    level = re.search('\/level:(.+?)\/', msg_content).group(1) if 'level:' in msg_content else "unknown"
                    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ColorPrinter.red("|" + msg_type_zh + "| " + self.align_left_str(nickname,20," ") + self.align_left_str("<Lv:" + level + ">",8," ") + self.align_left_str("("+ user_id +")",13," ") + self.align_left_str("["+strength+"]",10," ") + "@ "+time)

                elif msg_type == "dgb":
                    msg_type_zh = "礼物赠送"
                    level = re.search('\/level:(\d+?)\/', msg_content).group(1) if 'level:' in msg_content else "unknown"
                    user_id = re.search('\/uid:(.+?)\/', msg_content).group(1) if 'uid:' in msg_content else "unknown"
                    nickname = re.search('\/nn:(.+?)\/', msg_content).group(1) if 'nn:' in msg_content else "unknown"
                    strength = re.search('\/str:(.+?)\/', msg_content).group(1) if 'str:' in msg_content else "unknown"
                    dw = re.search('\/dw:(.+?)\/', msg_content).group(1) if 'dw:' in msg_content else "unknown"
                    gs = re.search('\/gs:(.+?)\/', msg_content).group(1) if 'gs:' in msg_content else "unknown"
                    hits = re.search('\/hits:(.+?)\/', msg_content).group(1) if 'hits:' in msg_content else "unknown"
                    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ColorPrinter.yellow("|" + msg_type_zh + "| " + self.align_left_str(nickname,20," ") + self.align_left_str("<Lv:" + level + ">",8," ") + self.align_left_str("("+ user_id +")",13," ") + self.align_left_str("[" + dw + "]",10," ") + self.align_left_str("[" + gs + "]",10," ") + self.align_left_str("[" + strength + "]",10," ") + "@ "+time+": " + hits + " hits ")
            except Exception as e:
                print(e)
                print("解析错误")




    def parse_content(self,msg):
        # print(msg)
        content = msg[12:-1].decode('utf-8','ignore')
        return content

    def danmu_recv(self):
        return self.parse_content(self.danmu_socket.recv(4000))

    def auth_recv(self):
        return self.parse_content(self.danmu_auth_socket.recv(4000))

    def send_auth_keeplive_msg(self):
        data = "type@=keeplive/tick@=" + self.timestamp() + "/vbw@=0/k@=19beba41da8ac2b4c7895a66cab81e23/"
        msg = self.message(data)
        self.danmu_auth_socket.sendall(msg)

    def send_danmu_keeplive_msg(self):
        data = "type@=keeplive/tick@=" + self.timestamp() + "/"
        msg = self.message(data)
        self.danmu_socket.sendall(msg)


    def send_danmu_join_group_msg(self):
        data  = "type@=joingroup/rid@=" + self.room_id + "/gid@="+ self.gid + "/"
        msg = self.message(data)
        self.danmu_socket.sendall(msg)

    def send_qrl_msg(self):
        data  = "type@=qrl/rid@=" + self.room_id + "/"
        msg = self.message(data)
        self.danmu_auth_socket.sendall(msg)

    def send_danmu_loginreq_msg(self):
        data = "type@=loginreq/username@="+self.username+"/password@=1234567890123456/roomid@=" + self.room_id + "/"
        msg = self.message(data)
        self.danmu_socket.sendall(msg)

    def send_auth_loginreq_msg(self):
        time = self.timestamp()
        vk = hashlib.md5(bytes(time + "7oE9nPEG9xXV69phU31FYCLUagKeYtsF" + self.dev_id,'utf-8')).hexdigest()
        data = "type@=loginreq/username@=/ct@=0/password@=/roomid@="+self.room_id+"/devid@="+self.dev_id + "/rt@="+self.timestamp()+"/vk@="+vk+"/ver@=20150929/"
        msg = self.message(data)
        self.danmu_auth_socket.sendall(msg)

    def timestamp(self):
        return str(int(time.time()))

    def message(self,content):
        return DouyuMsg(content).get_bytes()

    def align_left_str(self,raw_str,max_length,filled_chr):
        my_length = 0
        for i in range(0,len(raw_str)):
            if ord(raw_str[i]) > 127 or ord(raw_str[i]) <=0 :
                my_length += 1

            my_length += 1

        if (max_length - my_length) > 0:
            return raw_str + filled_chr * ( max_length - my_length )
        else:
            return raw_str


