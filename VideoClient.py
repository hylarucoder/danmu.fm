import requests, time, hashlib, json

BASE_URL = 'http://douyu.com/api/v1/'

class VideoClient(object):
    def __init__(self, roomId):
        self.roomId = roomId
        self.available = False
        self.urlList = []
    def fetch(self):
        url = 'room/%s?aid=android&client_sys=android&time=%s'%(self.roomId, str(int(time.time())))
        auth = hashlib.md5(bytes(url + '1231')).hexdigest()
        url = BASE_URL + '%s&auth=%s'%(url, auth)
        j = requests.get(url).json()['data']
        self.roomId = j['room_id']
        if not j['rtmp_url']:
            self.available = False
        else:
            self.available = True
            rtmpList = (j.get('rtmp_multi_bitrate', {}) or {}).values()[::-1] + [j['rtmp_live']]
            self.urlList = []
            for rtmp in rtmpList:
                url = '%s/%s'%(str(j["rtmp_url"]), rtmp)
                self.urlList.append(requests.get(url, allow_redirects=False).headers["Location"])
        return self.available

if __name__ == '__main__':
    v = VideoClient(16789)
    v.fetch()
    print v.roomId, v.available
    print v.urlList
