from datetime import datetime, timedelta
import json
import requests
import copy


def test_if():
    windows = {}
    if windows:
        print("windows is not empty")
    else:
        print("windows is empty")


def test_datetime():
    print(datetime.now())
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print(datetime.now() - timedelta(days=1))


def test_json():
    list = [{"a": 1, "b": 2}, {"a": 2, "b": 3}]
    new_list = [{"a": item["a"] + 1} for item in list]
    print(new_list)


def test_web():
    requests.post(f"http://0.0.0.0:5001/wechat/set_msg_ineffective", json={
        "id": "123123412341234123"
    })
    response = requests.get(f"http://0.0.0.0:5001/wechat/listen_new_msgs")
    print(response.json())
    
def test_copy():
    original_dict = {"a": 1, "b": 2, "c": {"d": 4}}
    new_dict = copy.deepcopy(original_dict)
    new_dict["a"] = 100
    print(original_dict)
    print(new_dict)


if __name__ == "__main__":
    test_copy()
