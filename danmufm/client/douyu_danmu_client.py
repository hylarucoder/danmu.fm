import datetime
import re
import uuid
import hashlib
import socket
import threading
import time
from misc.color_printer import ColorPrinter
from model.douyu_msg import DouyuMsg
# import sys
import logging

logger = logging.getLogger("danmufm")
class DouyuDanmuClient(object):

    """Docstring for DouyuDanmuClient. """

    def __init__(self,room,auth_dst_ip,auth_dst_port):
        self.DANMU_ADDR = ("danmu.douyutv.com",8602)
        self.DANMU_AUTH_ADDR = (auth_dst_ip,int(auth_dst_port))
        self.room = room
        self.room_id = str(room["id"])
        self.auth_dst_ip = auth_dst_ip
        self.auth_dst_port = auth_dst_port
        self.dev_id = str(uuid.uuid4()).replace("-","")


    def start(self):
        self.do_login()
        if self.live_stat == "离线":
            print("主播离线中,正在退出...")
        else:
            print("主播在线中,准备获取弹幕...")
            t = threading.Thread(target=self.keeplive)
            t.setDaemon(True)
            t.start()
            while True:
                self.get_danmu()

    def keeplive(self):
        print("启动 KeepLive 线程")
        while True:
            self.send_auth_keeplive_msg()
            self.send_danmu_keeplive_msg()
            # print("发送 KeepLive")
            time.sleep(40)






    def do_login(self):
        self.danmu_auth_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.danmu_auth_socket.connect(self.DANMU_AUTH_ADDR)
        self.danmu_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.danmu_socket.connect(self.DANMU_ADDR)
        self.send_auth_loginreq_msg()
        recv_msg = self.auth_recv()
        # print(recv_msg)
        if "live_stat@=0" in recv_msg:
            self.live_stat = "离线"
        else:
            self.live_stat = "在线"
            self.username = re.search('\/username@=(.+)\/nickname', recv_msg).group(1)
            recv_msg = self.auth_recv()
            self.gid = re.search('\/gid@=(\d+)\/', recv_msg).group(1)
            self.weight = re.search('\/weight@=(\d+)\/', recv_msg).group(1)
            self.fans_count = re.search('\/fans_count@=(\d+)\/', recv_msg).group(1)
            self.send_qrl_msg()
            recv_msg = self.auth_recv()
            # print(recv_msg)
            recv_msg = self.auth_recv()
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
            msg_type = re.search('type:(.+?)\/', msg_content).group(1)
            if msg_type == "chatmessage":
                msg_type_zh = "弹幕消息"
                sender_id = re.search('\/sender:(.+?)\/', msg_content).group(1)
                nickname = re.search('\/snick:(.+?)\/', msg_content).group(1)
                content = re.search('\/content:(.+?)\/', msg_content).group(1)
                strength = re.search('\/strength:(.+?)\/', msg_content).group(1)
                level = re.search('\/level:(.+?)\/', msg_content).group(1)
                time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ColorPrinter.green("|" + msg_type_zh + "| " + self.align_left_str(nickname,20," ") + self.align_left_str("<Lv:" + level + ">",8," ") + self.align_left_str("("+ sender_id +")",13," ") + self.align_left_str("["+strength+"]",10," ") + "@ "+time+": " + content +" ")

            elif msg_type == "userenter":
                msg_type_zh = "入房消息"
                user_id = re.search('\/userinfo:id:(.+?)\/', msg_content).group(1)
                nickname = re.search('\/nick:(.+?)\/',msg_content).group(1)
                strength = re.search('\/strength:(.+?)\/',msg_content).group(1)
                time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                level = re.search('\/level:(.+?)\/', msg_content).group(1)
                ColorPrinter.red("|" + msg_type_zh + "| " + self.align_left_str(nickname,20," ") + self.align_left_str("<Lv:" + level + ">",8," ") + self.align_left_str("("+ user_id +")",13," ") + self.align_left_str("["+strength+"]",10," ") + "@ "+time)

            elif msg_type == "dgn":
                msg_type_zh = "鱼丸赠送"
                level = re.search('\/level:(\d+?)\/', msg_content).group(1)
                user_id = re.search('\/sid:(.+?)\/', msg_content).group(1)
                nickname = re.search('\/src_ncnm:(.+?)\/', msg_content).group(1)
                hits = re.search('\/hits:(.+?)\/', msg_content).group(1)
                time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ColorPrinter.yellow("|" + msg_type_zh + "| " + self.align_left_str(nickname,20," ") + self.align_left_str("<Lv:" + level + ">",8," ") + self.align_left_str("("+ user_id +")",13," ") + self.align_left_str("[unknown]",10," ") + "@ "+time+": " + hits + " hits ")




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


