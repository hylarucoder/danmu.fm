class XimalayaClient(object):

    """

    喜马拉雅的设计差不多是Rest

    主播信息地址
    http://www.ximalaya.com/zhubo/3945648
    专辑列表
    http://www.ximalaya.com/3945648/album/
    专辑详细信息
    http://www.ximalaya.com/3945648/album/249020
    每一首声音的地址
    http://www.ximalaya.com/3945648/sound/12238413
    """

    XIMALAYA_ADDR = "http://www.ximalaya.com/zhubo/3945648"
    XIMALAYA_ZHUBO_ADDR = "http://www.ximalaya.com/zhubo/3945648"
    XIMALAYA_ALBUM_ADDR = "http://www.ximalaya.com/zhubo/3945648"
    XIMALAYA_SOUND_ADDR = "http://www.ximalaya.com/zhubo/3945648"


    def __init__(self,url):
        self.zhubo = {}
        self.zhubo["id"]
        self.zhubo["name"]
        self.zhubo["is_v"]
        self.zhubo["introduction"]
        self.zhubo["fans_count"]
        self.zhubo["album_count"]
        self.zhubo["sounds_count"]


