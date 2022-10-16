import requests
import json
import datetime
import argparse
import time
import threading

def get_config():
    with open("./post_me.json", "r") as f:
        text = json.loads(f.read())
    config, start_time, end_time = text["config"], text["start_time"], text["end_time"]
    config["order_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return config, start_time, end_time

class ReThreading():
    def __init__(self, start_time, end_time) -> None:
        self.start_time = start_time
        self.end_time = end_time
        self.is_success = False

    def post_reservation(self, config, id:int):
        url = "http://reservation.ruichengyunqin.com/api/blade-app/qywx/saveOrder?userid=" + config["student_id"]
        p_data = {
            "userNum":config["num_people"],
            "customerEmail":"",
            "gymId":"1297443858304540673",
            "gymName":"润杨羽毛球馆",
            "groundId":config["ground_id"][str(id)],
            "groundType":"0",
            "messagePushType":"0",
            "isIllegal":"0",
            "orderDate":config["order_time"],
            "startTime":self.start_time,
            "endTime":self.end_time,
            "tmpOrderDate":config["order_time"],
            "tmpStartTime":self.start_time,
            "tmpEndTime":self.end_time
        }
        if self.is_success:
            print("已经预定成功，无需预定！")
            return
        re = requests.post(url, data=json.dumps(p_data), headers={"Content-Type": "application/json"})
        re = json.loads(re.text)
        if re["success"]:
            self.is_success = True
            print(str(id)+"号场地预定成功！", "时间："+self.start_time+"  -  "+self.end_time)
        else:
            print(str(id)+"号场地预定失败! ", "时间："+self.start_time+"  -  "+self.end_time, " 原因："+re["msg"])
        
    def post_threading(self, config):
        for i in range(len(config["ground_id"])):
            t = threading.Thread(target=self.post_reservation, args=(config, i+1))
            t.start()
            time.sleep(0.1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='羽毛球场馆预定')
    parser.add_argument('re_type', type=int, help="模式选择参数: 0-固定时间模式, 1-手动回车模式")
    args = parser.parse_args()

    config, start_time, end_time = get_config()
    rethreadings = [ReThreading(i,j) for i,j in zip(start_time, end_time)]

    print("开始预定:", "固定时间模式" if args.re_type==0 else "手动回车模式")
    while True:
        if args.re_type == 1:
            print("==================按一次回车，预定一次========================")
            input()
            for rethreading in rethreadings:
                rethreading.post_threading(config)
        else: 
            now_time = datetime.datetime.now()
            set_time = datetime.datetime.strptime(config["set_time"],"%Y-%m-%d %H:%M:%S")
            print("==================距离设定时间还有: %s========================" %(set_time-now_time))
            if (set_time-now_time).seconds<=10 or (now_time-set_time).seconds<=20: # 到达设定时间，时间范围为30s
                for rethreading in rethreadings:
                    rethreading.post_threading(config)
                time.sleep(1)
            elif now_time<set_time and (set_time-now_time).seconds > 5: # 没到时间，每1s查询一次
                time.sleep(1)
