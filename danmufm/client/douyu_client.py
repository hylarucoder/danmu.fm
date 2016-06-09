import json
import re
from .douyu_danmu_client import DouyuDanmuClient
from urllib.request import urlopen
from urllib.parse import unquote
class DouyuClient:

    """Docstring for DouyuClient. """

    def __init__(self,url,g_config):
        self.DOUYU_PREFIX = "http://www.douyu.com/"

        if self.DOUYU_PREFIX not in url:
            url = self.DOUYU_PREFIX + url
        html = urlopen(url).read().decode()
        room_info_json = re.search('var\s\$ROOM\s=\s({.*});', html).group(1)
        # print(room_info_json)
        auth_server_json = re.search('\$ROOM\.args\s=\s({.*});', html).group(1)
        # print(auth_server_json)
        room_info_json_format = valid_json(room_info_json)
        auth_server_json_format = valid_json(auth_server_json)

        if room_info_json_format != False and auth_server_json_format != False:
            js = room_info_json_format
            room = {}
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
                for i in range(0,room_tags_size):
                    room["tags"].append(room_tags_json[js["room_tag_list"][i]]["name"])

            auth_servers = valid_json(unquote(auth_server_json_format["server_config"]))
            auth_server_ip = auth_servers[0]["ip"]
            auth_server_port = auth_servers[0]["port"]
            client = DouyuDanmuClient(room,auth_server_ip, auth_server_port,g_config)
            client.start()
        else:
            print("请求网页错误,正在退出...")

def valid_json(my_json):
    try:
        json_object = json.loads(my_json)
    except ValueError as e:
        print(e)
        return False
    return json_object



def main():
    DouyuClient("http://www.douyutv.com/236274")


if __name__ == "__main__":
    main()


