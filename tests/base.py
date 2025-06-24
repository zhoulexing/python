from datetime import datetime, timedelta

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
    json_data = {"a": 1, "b": 2}
    json_list = [json_data, {"a": 2, "b": 3}]
    json_list.extend([{"a": 3, "b": 4}])
    print(json_list)
    print(json_data.get("a"), len(json_list))
    new_json_list = [{'a': item["a"] + 1} for item in json_list]
    print(new_json_list)
    
    arr_list = []
    arr_list.append([1, 2, 3])
    arr_list.append([4, 5, 6])
    print(arr_list)

if __name__ == "__main__":
    test_json()