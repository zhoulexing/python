from pywxdump.db import MicroHandler
from pywxdump import get_wx_info, decrypt_merge
from pywxdump import WX_OFFS, DBHandler
import os
import time
import json


class WxHelperCore:
    def __init__(self):
        self.wx_info = get_wx_info(WX_OFFS)
        print(f"wx_info: {self.wx_info}")
        output_path = os.path.join(
            os.path.dirname(__file__), "assets", "wx_db")
        code, merge_save_path = decrypt_merge(
            self.wx_info[0]['wx_dir'], self.wx_info[0]['key'], output_path)
        print(f"decrypt_merge_result: {code}, {merge_save_path}")
        self.merge_save_path = merge_save_path

    def find_wxid_from_merged_db(self, nickname=None, remark=None):
        """
        在合并后的数据库中根据昵称或备注查找用户的 wxid。

        :param db_path: 已解密并合并的数据库文件路径 (e.g., merge_all.db)。
        :param nickname: 要搜索的联系人昵称 (可选)。
        :param remark: 要搜索的联系人备注 (可选)。
        """
        db_path = os.path.join(
            os.path.dirname(__file__), "assets", "wx_db", "merge_1750660380.db")
        if not os.path.exists(db_path):
            print(f"[-] 错误: 数据库文件不存在 {db_path}")
            return

        if not nickname and not remark:
            print("[-] 错误: 请至少提供一个搜索条件 (昵称或备注)。")
            return

        # 合并后的数据库包含了Contact表，所以我们可以直接使用MicroHandler
        db_config = {
            "key": "701b14190ca54f76ba86deef6b308d9e68fd9d8a01134e90b656ed4b3a9348f5",  # 对于已解密的数据库，key内容不敏感
            "type": "sqlite",
            "path": db_path
        }

        try:
            micro_handler = MicroHandler(db_config)

            # 确认Contact表是否存在
            if not micro_handler.tables_exist("Contact"):
                print(
                    f"[-] 错误: 在数据库 '{os.path.basename(db_path)}' 中未找到 'Contact' 表。")
                print("    请确保这是一个正确的、已合并的数据库文件。")
                return

            search_term = nickname if nickname else remark
            print(
                f"[+] 正在用关键词 '{search_term}' 在 {os.path.basename(db_path)} 中搜索联系人...")

            # get_user 方法会对昵称和备注进行模糊搜索
            contacts = micro_handler.get_user(word=search_term)

            if not contacts:
                print("[-] 没有找到匹配的联系人。")
                return

            print("\n[+] 找到以下匹配的联系人:")
            print("-" * 50)
            for wxid, user_info in contacts.items():
                print(f"  昵称 (NickName): {user_info.get('NickName', 'N/A')}")
                print(f"  备注 (Remark):   {user_info.get('Remark', 'N/A')}")
                print(f"  Wxid (UserName): {user_info.get('UserName', 'N/A')}")
                print(f"  头像 (Avatar):   {user_info.get('Avatar', 'N/A')}")
                print("-" * 50)

        except Exception as e:
            print(f"[-] 查询时发生错误: {e}")

    def export_chat_history_to_json(self, contact_wxid, start_time_str, end_time_str, output_path):
        """
        导出指定联系人在指定时间段内的聊天记录为JSON文件。

        :param merge_db_path: 合并后的数据库文件路径 (merge_all.db)
        :param contact_wxid: 联系人的wxid
        :param start_time_str: 开始时间，格式为 "YYYY-MM-DD HH:MM:SS"
        :param end_time_str: 结束时间，格式为 "YYYY-MM-DD HH:MM:SS"
        :param output_path: JSON文件输出路径
        """
        if not os.path.exists(self.merge_save_path):
            print(f"[-] 错误: 数据库文件不存在 {self.merge_save_path}")
            return

        # 将时间字符串转换为时间戳
        try:
            start_timestamp = int(time.mktime(
                time.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")))
            end_timestamp = int(time.mktime(
                time.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")))
        except ValueError:
            print("[-] 错误: 时间格式不正确，请使用 'YYYY-MM-DD HH:MM:SS'")
            return

        # 初始化DBHandler
        # 注意：这里的db_config需要一个唯一的key，但对于已解密的数据库，内容不敏感
        db_config = {
            "key": self.wx_info[0]['key'],
            "type": "sqlite",
            "path": self.merge_save_path
        }
        db_handler = DBHandler(db_config)

        # 获取总消息数以进行分页
        msg_counts = db_handler.get_m_msg_count(contact_wxid)
        total_msgs = msg_counts.get(contact_wxid, 0)
        if total_msgs == 0:
            print(f"[-] wxid为'{contact_wxid}'的联系人没有聊天记录。")
            return

        print(f"[+] 正在获取 {contact_wxid} 的聊天记录，共约 {total_msgs} 条...")

        # 使用get_msg_list并传入时间戳
        # 设置一个足够大的page_size来获取所有消息
        all_messages, users = db_handler.get_msg_list(
            wxids=contact_wxid,
            start_index=0,
            page_size=total_msgs,  # 一次性获取所有消息
            start_createtime=start_timestamp,
            end_createtime=end_timestamp
        )

        if not all_messages:
            print(f"[-] 在指定时间范围内没有找到与 {contact_wxid} 的聊天记录。")
            return

        # 准备要导出的数据
        export_data = {
            "contact_wxid": contact_wxid,
            "time_range": {
                "start": start_time_str,
                "end": end_time_str
            },
            "message_count": len(all_messages),
            "messages": all_messages,
            "related_users": users
        }

        # 导出到JSON文件
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=4)
            print(f"[+] 成功将 {len(all_messages)} 条聊天记录导出到 {output_path}")
        except IOError as e:
            print(f"[-] 错误: 无法写入文件 {output_path}. 原因: {e}")


if __name__ == "__main__":
    wx_helper_core = WxHelperCore()
    # ======== 如何通过昵称查找 wxid ========
    # 在下方输入你想要查找的昵称
    wx_helper_core.find_wxid(nickname="文件传输助手")

    # # ======== 如何导出聊天记录 ========
    # # 1. 先用上面的方法找到wxid
    # # 2. 在下方填入wxid和时间范围
    # wx_helper_core.export_chat_history_to_json(
    #     contact_wxid="filehelper", # 替换为你要导出的联系人wxid
    #     start_time_str="2024-01-01 00:00:00",
    #     end_time_str="2024-07-25 23:59:59",
    #     output_path=os.path.join(os.path.dirname(__file__), "assets", "chat_history_export.json")
    # )
