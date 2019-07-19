import requests
import json
import time


# 订购日期
order_date = "2019-07-22"
# 订购起始时间
start_time = 17
# 订购场次



# 配置cookie、订场日期
# cookie = "ASP.NET_SessionId=sk1eggjsb1ypjqtird2yloga"
cookie = "ASP.NET_SessionId=0vshqwzrjoktorl1cahu203v"

headers = {"cookie": cookie,
           "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, "
                         "like Gecko) Mobile/15E148 MicroMessenger/7.0.4(0x17000428) NetType/WIFI Language/zh_CN"}
# 查询场地信息接口
ground_info_url = "http://wx.szbicc.net/SZW/VenueBill/ApiGetVenueStatus"
# 下单接口
order_url = "http://wx.szbicc.net/SZW/VenueBill/ApiVenueBill"
# 获取钱包信息接口
url = "http://wx.szbicc.net/SZW/VenueBill/ApiGetVenueBillPos"
# 支付接口
sumbit_url = "http://wx.szbicc.net/SZW/VenueBill/ApiVenueBillOK"


# 查询5:00~6:30可用的场次索引
def get_free_ground_index(groud_arry):
    # 一共30个场地
    # 时间17：00，连续3个时间段
    begin = (17 - 9) * 2 * 30
    for x in range(30):
        if (groud_arry[begin + x]["IsFree"] and groud_arry[begin + x + 30]["IsFree"] and groud_arry[begin + x + 60][
            "IsFree"]):
            return begin + x
        else:
            continue
    return None


if __name__ == '__main__':
    # 轮询当日场次
    ground_index = None
    print(time.strftime('%Y-%m-%d %H:%M:%S'))
    while (ground_index is None):
        try:
            time.sleep(1)
            print("查询场地...")
            res_ground = requests.post(ground_info_url, data={"VenueType": "69DE6212-EA1A-4326-B764-98ABC2B5F190",
                                                              "BillDay": order_date}, headers=headers)
            if (json.loads(res_ground.text)["code"] != "0"):
                # 登录失效，发送通知
                requests.get("https://api.day.app/fuZXJ8GHrXNHEkTREiNMr5/登录失效了")
                break
            ground_array = json.loads(json.loads(res_ground.text)["data"])
            ground_index = get_free_ground_index(ground_array)
        except Exception as e:
            print(e)

    if (ground_index is not None):
        print("准备预定" + str(ground_index % 30 + 1) + "号场")
        print(ground_array[ground_index])
        print(ground_array[ground_index + 30])
        print(ground_array[ground_index + 60])
        # 构造订单参数
        order_data = {}
        order_data["VenueIcon"] = 131
        order_data["BillDay"] = order_date
        order_data["Details[0][Venue]"] = ground_array[ground_index]["Venue"]
        order_data["Details[0][StartTime]"] = ground_array[ground_index]["StartTime"]
        order_data["Details[0][BillTime]"] = ground_array[ground_index]["BillTime"]
        order_data["Details[0][BillMoney]"] = ground_array[ground_index]["Price"]

        order_data["Details[1][Venue]"] = ground_array[ground_index + 30]["Venue"]
        order_data["Details[1][StartTime]"] = ground_array[ground_index + 30]["StartTime"]
        order_data["Details[1][BillTime]"] = ground_array[ground_index + 30]["BillTime"]
        order_data["Details[1][BillMoney]"] = ground_array[ground_index + 30]["Price"]

        order_data["Details[2][Venue]"] = ground_array[ground_index + 60]["Venue"]
        order_data["Details[2][StartTime]"] = ground_array[ground_index + 60]["StartTime"]
        order_data["Details[2][BillTime]"] = ground_array[ground_index + 60]["BillTime"]
        order_data["Details[2][BillMoney]"] = ground_array[ground_index + 60]["Price"]

        order_code = "-1"
        while (order_code == "-1"):
            try:
                time.sleep(2)
                # 下单
                print("下单")
                res_order = requests.post(order_url, data=order_data, headers=headers)
                # 订单编号
                order_code = json.loads(res_order.text)["code"]
                print(json.loads(res_order.text))
            except Exception as e:
                print(e)

        order_no = json.loads(res_order.text)["data"]
        # 订单地址
        print("http://wx.szbicc.net/SZW/VenueBill/VenueBillConfirmWX?RecordNo=" + order_no)

        pre_pay_code = "-1"
        while (pre_pay_code == "-1"):
            try:
                time.sleep(1)
                # 获取支付信息
                print("准备支付")
                # 获取钱包信息
                wait_pay_order = requests.post(url, data={"RecordNo": order_no}, headers=headers)
                res_msg = json.loads(wait_pay_order.text)
                pre_pay_code = res_msg["code"]
                print(res_msg)
            except Exception as e:
                print(e)

        SysApp = json.loads(res_msg["data"])["Details"][0]["SysApp"]
        BillValue = json.loads(res_msg["data"])["Details"][0]["PosValue"]

        # 支付
        sub_code = "-1"
        while (sub_code == "-1"):
            try:
                # 支付
                print("支付")

                sub = requests.post(sumbit_url, data={"RecordNo": order_no, "SysApp": SysApp, "BillValue": BillValue},
                                    headers=headers)
                print(sub.text)
                sub_code = json.loads(sub.text)["code"]
            except Exception as e:
                print(e)

        # 手机通知
        requests.get(
            "https://api.day.app/fuZXJ8GHrXNHEkTREiNMr5/预定成功?automaticallyCopy=1&copy=http://wx.szbicc.net/SZW/VenueBill/VenueBillConfirmWX?RecordNo=" + order_no)
