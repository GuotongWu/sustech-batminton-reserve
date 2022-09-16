import requests
import json
import datetime
import argparse
import time
import threading

ground_id = {
    1: "1298272433186332673",
    2: "1298272520994086913",
    3: "1298272615009411073",
    4: "1298272709167341570",
    5: "1298272791098875905",
    6: "1298273087183183874",
    7: "1298273175146127362",
    8: "1298273265650819073",
    9: "1298273399927267330",
    10: "1298273500317933570"
}

event = threading.Event()

def get_config():
    with open("./post.json", "r") as f:
        config = json.loads(f.read())
    config["order_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return config

def post_reservation(config, id:int):
    url = "http://reservation.ruichengyunqin.com/api/blade-app/qywx/saveOrder?userid=" + config["student_id"]
    p_data = {
        "userNum":config["num_people"],
        "customerEmail":"",
        "gymId":"1297443858304540673",
        "gymName":"润杨羽毛球馆",
        "groundId":ground_id[id],
        "groundType":"0",
        "messagePushType":"0",
        "isIllegal":"0",
        "orderDate":config["order_time"],
        "startTime":config["start_time"],
        "endTime":config["end_time"],
        "tmpOrderDate":config["order_time"],
        "tmpStartTime":config["start_time"],
        "tmpEndTime":config["end_time"]
        }
    if event.is_set():
        print("已经预定成功，无需预定！")
        return
    re = requests.post(url, data=json.dumps(p_data), headers={"Content-Type": "application/json"})
    re = json.loads(re.text)
    if re["success"]:
        event.set()
        print(str(id)+"号场地预定成功！")
    else:
        print(str(id)+"号场地预定失败！")

def post_threading():
    for i in range(len(ground_id)):
        t = threading.Thread(target=post_reservation, args=(config, i+1))
        t.start()
        time.sleep(0.2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='羽毛球场馆预定')
    parser.add_argument('re_type', type=int, help="模式选择参数: 0-固定时间模式, 1-手动回车模式")
    args = parser.parse_args()

    config = get_config()
    print("开始预定:", "固定时间模式" if args.re_type==0 else "手动回车模式")
    while True:
        if args.re_type == 1:
            print("==================按一次回车，预定一次========================")
            input()
            post_threading()
        else: 
            now_time = datetime.datetime.now()
            delta_time = datetime.datetime.strptime(config["set_time"],"%Y-%m-%d %H:%M:%S") - now_time
            print("==================距离设定时间还有: %s========================" %(delta_time))
            if delta_time.seconds < 5: # 如果与设定时间小于5s，开抢
                post_threading()
            else: # 否则每一秒查询一次
                time.sleep(1)
        if event.is_set():
            break