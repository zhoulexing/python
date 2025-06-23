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


if __name__ == "__main__":
    test_datetime()