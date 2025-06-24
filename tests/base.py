from datetime import datetime, timedelta
import json
import requests


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


if __name__ == "__main__":
    test_web()
