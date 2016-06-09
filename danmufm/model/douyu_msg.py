class DouyuMsg(object):

    """Docstring for DouyuMsg. """

    def __init__(self,content):
        self.length = bytearray([len(content) + 9, 0x00, 0x00, 0x00])
        self.code = self.length
        self.magic = bytearray([0xb1, 0x02, 0x00, 0x00])
        self.content = bytes(content.encode("utf-8"))
        self.end = bytearray([0x00])


    def get_bytes(self):
        return bytes(self.length + self.code + self.magic + self.content + self.end)


if __name__ == "__main__":
    print(DouyuMsg("type").get_bytes())

