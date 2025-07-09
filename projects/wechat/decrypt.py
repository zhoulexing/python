from pywxdump import get_wx_info, decrypt_merge, all_merge_real_time_db, get_core_db, decrypt
from pywxdump import WX_OFFS, DBHandler
import os
import random
import string
import json
from utils.config import Config

config = Config()


class WeChatDecrypt:
    def __init__(self):
        # 此方法能获取登录微信的账号信息和关键密钥key
        self.wx_info = self.get_wx_info()
        # 合并后的数据库文件路径
        self.merge_db_file = os.path.join(
            os.path.dirname(__file__), "../../assets/wx_db/merge_1750666183.db")
        # 消息数据库文件路径
        self.msg_db_file = os.path.join(
            os.path.dirname(__file__), "../../assets/wx_db/msg.db")
        # 消息数据库索引
        self.msg_db_index = config.get("wx_msg_db_index")

    def random_str(self, num=16):
        return ''.join(random.sample(string.ascii_letters + string.digits, num))

    def get_wx_info(self):
        wx_infos = get_wx_info(WX_OFFS)
        if len(wx_infos) > 0:
            config.set("wxinfo", json.dumps(wx_infos[0]))
            return wx_infos[0]
        raise Exception("[-] 未找到微信信息, 请重新登录")

    def decrypt_merge(self):
        output_path = os.path.join(
            os.path.dirname(__file__), "../../assets/wx_db")

        # 解密多个数据库并合并成一个到output_path目录下
        success, merge_db_file = decrypt_merge(
            self.wx_info['wx_dir'], self.wx_info['key'], output_path)
        print(f"decrypt_merge_result: {success}, {merge_db_file}")
        if not success:
            raise Exception("[-] 解密失败, 请检查key是否正确")
        self.merge_db_file = merge_db_file

    def decrypt_msg(self):
        # 获取微信数据库路径
        success, wxdbpaths = get_core_db(self.wx_info['wx_dir'], ["MSG"])
        if not success:
            raise Exception("[-] 获取数据库路径失败")
        print(f"wxdbpaths: {wxdbpaths[0]}")
        print(f"key: {self.wx_info['key']}")
        success, list = decrypt(
            self.wx_info['key'], wxdbpaths[0]['db_path'], self.msg_db_file)
        print(f"list: {list}")
        if not success:
            raise Exception("[-] 解密失败, 请检查key是否正确")


    def all_merge_real_time_db(self):
        # 合并所有临时数据库，后面要轮询执行，实时拿到最新的消息
        code, ret = all_merge_real_time_db(key=self.wx_info['key'], wx_path=self.wx_info['wx_dir'], merge_path=self.merge_db_file,
                                           real_time_exe_path=None)
        print(f"all_merge_real_time_db_result: {code}, {ret}")
        if not code:
            raise Exception("[-] 合并失败, 请检查key是否正确")
        return ret

    def get_all_user(self):
        if not os.path.exists(self.merge_db_file):
            print(f"[-] 错误: 数据库文件不存在 {self.merge_db_file}")
            return

        db_config = {
            "key": self.random_str(16),
            "type": "sqlite",
            "path": self.merge_db_file
        }
        db = DBHandler(db_config, self.wx_info['wxid'])
        ret = db.get_session_list()
        return ret.values()

    def get_user_by_nickname(self, nickname):
        users = self.get_all_user()
        for user in users:
            if user.get("strNickName") == nickname:
                return user
        return None

    def get_msg_by_wxid(self, wxid):
        db_config = {
            "key": self.random_str(16),
            "type": "sqlite",
            "path": self.merge_db_file
        }

        db = DBHandler(db_config, self.wx_info['wxid'])
        start_index = int(config.get("wx_msg_db_index"))
        msgs, users = db.get_msgs(
            wxids=wxid, start_index=start_index, page_size=100)
        if len(msgs) > 0:
            config.set("wx_msg_db_index", msgs[-1]['id'])
        return msgs, users

    def find_new_msgs_of_robot(self, nickname):
        self.all_merge_real_time_db()
        user = self.get_user_by_nickname(nickname)
        msgs, users = self.get_msg_by_wxid(user['wxid'])
        msg_text_list = [{"role": "user", "content": item["msg"]}
                         for item in msgs if item["type_name"] == "文本" and item["is_sender"] != 1]
        return msg_text_list


if __name__ == "__main__":
    wechat_decrypt = WeChatDecrypt()
    wechat_decrypt.find_new_msgs_of_robot("测试2号xxxxx")
