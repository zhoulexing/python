from pywxdump import get_wx_info, decrypt_merge, all_merge_real_time_db
from pywxdump import WX_OFFS, DBHandler
import os
import random
import string
import json


class WeChatDecrypt:
    def __init__(self):
        # self.wx_info = self.get_wx_info()
        # print(f"wx_info: {self.wx_info}")
        self.wx_info = {
            'pid': 14736,
            'version': '3.9.10.27',
            'account': 'Youzan-timi',
            'mobile': '13282826803',
            'nickname': 'kimi',
            'mail': None,
            'wxid': 'wxid_mnrojdr78dhf12',
            'key': '701b14190ca54f76ba86deef6b308d9e68fd9d8a01134e90b656ed4b3a9348f5',
            'wx_dir': 'C:\\WeChat Files\\wxid_mnrojdr78dhf12'
        }
        # self.merge_save_path = None
        self.merge_save_path = os.path.join(
            os.path.dirname(__file__), "../../assets/wx_db/merge_1750666183.db")

    def random_str(self, num=16):
        return ''.join(random.sample(string.ascii_letters + string.digits, num))

    def get_wx_info(self):
        wx_infos = get_wx_info(WX_OFFS)
        if len(wx_infos) > 0:
            return wx_infos[0]
        raise Exception("[-] 未找到微信信息, 请重新登录")

    def decrypt_merge(self):
        output_path = os.path.join(
            os.path.dirname(__file__), "../../assets/wx_db")

        success, merge_save_path = decrypt_merge(
            self.wx_info['wx_dir'], self.wx_info['key'], output_path)
        print(f"decrypt_merge_result: {success}, {merge_save_path}")
        if not success:
            raise Exception("[-] 解密失败, 请检查key是否正确")
        self.merge_save_path = merge_save_path

    def all_merge_real_time_db(self):
        code, ret = all_merge_real_time_db(key=self.wx_info['key'], wx_path=self.wx_info['wx_dir'], merge_path=self.merge_save_path,
                                           real_time_exe_path=None)
        print(f"all_merge_real_time_db_result: {code}, {ret}")
        if not code:
            raise Exception("[-] 合并失败, 请检查key是否正确")
        return ret

    def get_all_user(self):
        if not os.path.exists(self.merge_save_path):
            print(f"[-] 错误: 数据库文件不存在 {self.merge_save_path}")
            return

        db_config = {
            "key": self.random_str(16),
            "type": "sqlite",
            "path": self.merge_save_path
        }
        db = DBHandler(db_config, self.wx_info['wxid'])
        ret = db.get_session_list()
        print(f"ret.values(): {ret.values()}")
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
            "path": self.merge_save_path
        }

        db = DBHandler(db_config, self.wx_info['wxid'])
        msgs, users = db.get_msgs(wxids=wxid, start_index=0, page_size=1000)
        return json.dumps(msgs), json.dumps(users)


if __name__ == "__main__":
    wechat_decrypt = WeChatDecrypt()

    # wx_helper_core.decrypt_merge()
    # user = wechat_decrypt.get_user_by_nickname("火麒麟")
    # msgs, users = wechat_decrypt.get_msg_by_wxid(user['wxid'])
    # print(f"msgs: {msgs}")


    wechat_decrypt.all_merge_real_time_db()