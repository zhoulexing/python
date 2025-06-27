from projects.wechat.ai import WeChatAi

wechat_ai = WeChatAi()

def test_agent():
    while True:
        print("\n请输入朋友圈文案（输入 exit 退出）：")
        text = input("文案：")
        if text.strip().lower() == "exit":
            wechat_ai.clear_messages()
            break
        sussess, text, image_urls = wechat_ai.run(message=text)
        if sussess:
            print(f"朋友圈文案和图片为: {text}, {image_urls}")
        
def test_execute():
    wechat_ai.add_message("user", "你好")
    result = wechat_ai.execute()
    print(f"wechat ai execute: {result}")

test_agent()