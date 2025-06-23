from pywxdump import get_wx_info, merge_db, decrypt_merge
from pywxdump import WX_OFFS
import os

class WxHelperCore:
    def __init__(self):
        self.wx_info = get_wx_info(WX_OFFS)
        print(f"wx_info: {self.wx_info}")
        self.db_path = merge_db(self.wx_info.wx_dir)
        print(f"db_path: {self.db_path}")
        output_path = os.path.join(os.path.dirname(__file__), "assets", "wx_db")
        decrypt_merge_result = decrypt_merge(self.wx_info.wx_dir, self.wx_info.key, output_path)
        print(f"decrypt_merge_result: {decrypt_merge_result}")

if __name__ == "__main__":
    wx_helper_core = WxHelperCore()