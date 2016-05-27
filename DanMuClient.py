import socket, json, re, thread
import uuid, hashlib, time
from urllib import unquote

import requests

class _socket(socket.socket):
    def __init__(self, *args, **kwargs):
        socket.socket.__init__(self, *args, **kwargs)
    def communicate(self, data):
        self.push(data)
        return self.pull()
    def push(self, data):
        data =  bytes(bytearray([len(data) + 9, 0x00, 0x00, 0x00]) * 2 + # length
            bytearray([0xb1, 0x02, 0x00, 0x00]) + # magic
            bytes(data.encode('utf-8')) + bytearray([0x00]))
        self.sendall(data)
    def pull(self):
        return self.recv(9999)[12:-1].decode('utf8', 'ignore')

class DanMuClient(object):
    def __init__(self):
        self.url = ''
        self.roomId = -1
        self.live = False
        self.danmuSocket, self.authSocket = None, None
        self.msgPipe = []
    def start(self, url):
        roomInfo, authIp, authPort = self.load_room(url)
        self.roomId = roomInfo['room_id']
        self._socket_init(authIp, authPort)
        userName = self._get_user(roomInfo['room_id'])
        if userName is None: return False
        groupId = re.search('/gid@=(\d+)/', self.authSocket.pull()).group(1)
        self._enter_room(userName, roomInfo['room_id'])
        self._start_receive(roomInfo['room_id'], groupId)
        return True
    def load_room(self, url):
        content = requests.get(url).content
        roomInfo = json.loads(re.search('\$ROOM = ({[\s\S]*?});', content).group(1))
        authInfo = json.loads(re.search('\$ROOM.args = ({[\s\S]*?});', content).group(1))
        # This contains more than one ip, you may add ip test here.
        # I didn't and I won't because I'm lazy XD
        authServerInfo = json.loads(unquote(authInfo['server_config']))[0]
        return roomInfo, authServerInfo['ip'], int(authServerInfo['port'])
    def _socket_init(self, authIp, authPort):
        self.danmuSocket = _socket(socket.AF_INET, socket.SOCK_STREAM)
        self.authSocket = _socket(socket.AF_INET, socket.SOCK_STREAM)
        self.danmuSocket.connect(('danmu.douyutv.com', 8602))
        self.authSocket.connect((authIp, authPort))
    def _get_user(self, roomId):
        randomDevId = str(uuid.uuid4()).replace('-', '')
        timeStamp = str(int(time.time()))
        verifyKey = hashlib.md5(bytes(timeStamp +
            '7oE9nPEG9xXV69phU31FYCLUagKeYtsF' + randomDevId)).hexdigest()
        data = ('type@=loginreq/username@=/ct@=0/password@=/roomid@=%s/devid@=%s/rt@=' +
            '%s/vk@=%s/ver@=20150929/ltkid@=/biz@=/stk@=/')%(roomId, randomDevId, timeStamp, verifyKey)
        content = self.authSocket.communicate(data)
        if 'live_stat@=1' in content: return re.search('/username@=(.+?)/', content).group(1)
    def _keep_alive(self, type = 'both'):
        if type == 'danmu':
            self.danmuSocket.communicate('type@=keeplive/tick@=%s/'%str(int(time.time())))
        elif type == 'auth':
            self.authSocket.communicate(('type@=keeplive/tick@=%s/vbw@=0/' +
                'k@=19beba41da8ac2b4c7895a66cab81e23/')%str(int(time.time())))
        elif type == 'both':
            self._keep_alive('danmu')
            self._keep_alive('auth')
        else:
            print('Unknown keep-alive')
    def _enter_room(self, userName, roomId):
        self.authSocket.communicate('type@=qrl/rid@=%s/'%roomId) # auth enter room
        self._keep_alive('auth')
        # debug password
        self.danmuSocket.communicate(('type@=loginreq/username@=%s/password@=' +
            '1234567890123456/roomid@=%s/')%(userName, roomId))
    def _start_receive(self, roomId, groupId):
        self.danmuSocket.communicate(('type@=joingroup/rid@=%s' +
            '/gid@=%s/')%(roomId, groupId)) # enter group
        self.live = True
        def keep_alive(self):
            while self.live:
                self._keep_alive()
                time.sleep(30)
        def get_danmu(self):
            while 1:
                content = self.danmuSocket.pull()
                try:
                    sender = re.search('/nn@=(.*?)/', content).group(1)
                    s = re.search('/txt@=(.*?)/', content).group(1)
                except:
                    pass
                else:
                    self.msgPipe.append((sender, s))
        thread.start_new_thread(keep_alive, (self, ))
        thread.start_new_thread(get_danmu, (self, ))

if __name__ == '__main__':
    d = DanMuClient()
    # I don't mean it
    # This is only because YiLiDi is not live when I test this
    print d.start('http://www.douyu.com/214786')
    while 1:
        if d.msgPipe: print('[%s]: %s'%d.msgPipe.pop())
        time.sleep(.1)
