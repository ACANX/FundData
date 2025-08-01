#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
"""
import requests
import json
from time import sleep


class FundData(object):
    def __init__(self, code):
        self.code = code

    def getNPV(self):
        """
        查询全部历史净值
        :return: 查询结果字典，成功或者失败
        """
        page = 1
        url = "http://api.fund.eastmoney.com/f10/lsjz?callback=jQuery18304038998523093684_1586160530315"
        tempurl = url + "&fundCode={}&pageIndex={}&pageSize=20".format(self.code, page)
        header = {"Referer": "http://fundf10.eastmoney.com/jjjz_{}.html".format(self.code)}

        jsonData = requests.get(tempurl, headers=header).content.decode()
        dictData = json.loads(jsonData[41:-1])
        print("初次执行结果：\n{}".format(dictData))
        totalCount = dictData.get("TotalCount")

        tmpList = list()

        pageTotal = totalCount // 20
        if totalCount % 20 != 0:
            pageTotal += 1
        print("总页数为 {}".format(pageTotal))

        for singlePage in range(1, pageTotal+1):
            tempurl = url + "&fundCode={}&pageIndex={}&pageSize=20".format(self.code, singlePage)
            print("现在处理第 {} 页数据".format(singlePage))
            jsonData = requests.get(tempurl, headers=header).content.decode()
            dictData = json.loads(jsonData[41:-1])
            listDateData = dictData.get("Data", {"LSJZList": None}).get("LSJZList")
            for item in listDateData:
                # 获取日期
                npvDate = item.get("FSRQ")
                # 获取每日单位净值
                npv = item.get("DWJZ")
                # 获取每日增长率，基金最开始的一段时间为封闭期，增长率为0
                tempRate = item.get("JZZZL")
                rate = "0.00" if tempRate == "" else tempRate
                view = (self.code, str(npvDate), str(npv), str(rate))
                tmpList.append(view)
            sleep(1)

        return {"message": "ok", "status": 200}


fund = FundData('017516')
mes = fund.getNPV()
# 打印处理结果
print(mes)
