#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
"""
import requests
import json
from time import sleep
import os
import sys


class FundData(object):
    def __init__(self, code):
        self.code = code

    def getNPV(self):
        """
        查询全部历史净值
        :return: 包含数据和状态信息的字典
        """
        page = 1
        url = "http://api.fund.eastmoney.com/f10/lsjz?callback=jQuery18304038998523093684_1586160530315"
        tempurl = url + "&fundCode={}&pageIndex={}&pageSize=20".format(self.code, page)
        header = {"Referer": "http://fundf10.eastmoney.com/jjjz_{}.html".format(self.code)}

        try:
            jsonData = requests.get(tempurl, headers=header).content.decode()
            dictData = json.loads(jsonData[41:-1])
            print("初次执行结果：\n{}".format(dictData))
            totalCount = dictData.get("TotalCount")

            dataList = []  # 存储所有净值数据的列表

            pageTotal = totalCount // 20
            if totalCount % 20 != 0:
                pageTotal += 1
            print("总页数为 {}".format(pageTotal))

            # 处理第一页数据
            listDateData = dictData.get("Data", {"LSJZList": []}).get("LSJZList")
            for item in listDateData:
                npvDate = item.get("FSRQ")
                npv = item.get("DWJZ")
                tempRate = item.get("JZZZL")
                rate = "0.00" if tempRate == "" else tempRate
                
                dataList.append({
                    "fund_code": self.code,
                    "date": npvDate,
                    "net_asset_value": npv,
                    "daily_growth_rate": rate
                })

            # 处理剩余页数据
            for singlePage in range(2, pageTotal + 1):
                tempurl = url + "&fundCode={}&pageIndex={}&pageSize=20".format(self.code, singlePage)
                print("现在处理第 {} 页数据".format(singlePage))
                jsonData = requests.get(tempurl, headers=header).content.decode()
                dictData = json.loads(jsonData[41:-1])
                listDateData = dictData.get("Data", {"LSJZList": []}).get("LSJZList")
                for item in listDateData:
                    npvDate = item.get("FSRQ")
                    npv = item.get("DWJZ")
                    tempRate = item.get("JZZZL")
                    rate = "0.00" if tempRate == "" else tempRate
                    
                    dataList.append({
                        "fund_code": self.code,
                        "date": npvDate,
                        "net_asset_value": npv,
                        "daily_growth_rate": rate
                    })
                sleep(1)  # 避免请求过于频繁

            # 创建目录并保存JSON文件
            current_dir = os.path.dirname(os.path.abspath(__file__))
            save_dir = os.path.join(current_dir, "..", "Fund", "CN", "Data")
            os.makedirs(save_dir, exist_ok=True)  # 确保目录存在
            
            json_file = os.path.join(save_dir, f"{self.code}.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(dataList, f, ensure_ascii=False, indent=4)
                print(f"数据已保存到: {json_file}")

            return {
                "message": "ok",
                "status": 200,
                "data": dataList,
                "file_path": json_file
            }

        except Exception as e:
            return {
                "message": str(e),
                "status": 500,
                "data": [],
                "file_path": ""
            }


if __name__ == '__main__':
    fund = FundData('017516')
    result = fund.getNPV()
    # 打印处理结果
    print(f"状态: {result['status']}")
    print(f"消息: {result['message']}")
    print(f"保存路径: {result.get('file_path', '')}")
    print(f"获取数据条数: {len(result['data'])}")
