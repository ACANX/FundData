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
    
    def save_to_json(self, data):
        """
        将数据保存为JSON文件
        :param data: 要保存的数据
        :return: 文件保存路径
        """
        try:
            # 创建目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            save_dir = os.path.join(current_dir, "..", "Fund", "CN", "Data")
            os.makedirs(save_dir, exist_ok=True)
            
            # 构建文件路径
            json_file = os.path.join(save_dir, f"{self.code}.json")
            
            # 保存数据
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"基金 {self.code} 数据已保存到: {json_file}")
            
            return json_file
        except Exception as e:
            print(f"保存基金 {self.code} 数据时出错: {str(e)}")
            return None

    def getNPV(self):
        """
        查询全部历史净值
        :return: 净值数据列表
        """
        try:
            page = 1
            url = "http://api.fund.eastmoney.com/f10/lsjz?callback=jQuery18304038998523093684_1586160530315"
            tempurl = url + "&fundCode={}&pageIndex={}&pageSize=20".format(self.code, page)
            header = {"Referer": "http://fundf10.eastmoney.com/jjjz_{}.html".format(self.code)}

            # 发送初始请求获取总页数
            response = requests.get(tempurl, headers=header)
            response.raise_for_status()  # 检查HTTP错误
            jsonData = response.content.decode()
            
            # 解析JSON数据
            dictData = json.loads(jsonData[41:-1])
            totalCount = dictData.get("TotalCount", 0)
            
            if totalCount == 0:
                print(f"基金 {self.code} 未找到净值数据")
                return []

            dataList = []  # 存储所有净值数据的列表

            # 计算总页数
            pageTotal = totalCount // 20
            if totalCount % 20 != 0:
                pageTotal += 1
            print(f"基金 {self.code} 共有 {totalCount} 条数据，{pageTotal} 页")

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

            # 处理剩余页数据（如果有）
            if pageTotal > 1:
                for singlePage in range(2, pageTotal + 1):
                    tempurl = url + "&fundCode={}&pageIndex={}&pageSize=20".format(self.code, singlePage)
                    print(f"基金 {self.code} 正在处理第 {singlePage}/{pageTotal} 页数据")
                    
                    response = requests.get(tempurl, headers=header)
                    response.raise_for_status()
                    jsonData = response.content.decode()
                    
                    dictData = json.loads(jsonData[41:-1])
                    listDateData = dictData.get("Data", {"LSJZList": []}).get("LSJZList")
                    
                    for item in listDateData:
                        npvDate = item.get("FSRQ").replace("-", "")
                        npv = item.get("DWJZ")
                        tempRate = item.get("JZZZL")
                        rate = "0.00" if tempRate == "" else tempRate
                        
                        dataList.append({
                            "date": npvDate,
                            "nav": npv,
                            "change_rate": rate
                        })
                    
                    sleep(1.5)  # 降低请求频率，避免被封

            print(f"基金 {self.code} 成功获取 {len(dataList)} 条净值数据")
            return dataList

        except requests.exceptions.RequestException as e:
            print(f"基金 {self.code} 网络请求失败: {str(e)}")
            return []
        except json.JSONDecodeError as e:
            print(f"基金 {self.code} JSON解析失败: {str(e)}")
            return []
        except Exception as e:
            print(f"基金 {self.code} 处理过程中出错: {str(e)}")
            return []


def collect_fund_data(fund_codes):
    """
    收集多个基金的数据并保存
    :param fund_codes: 基金代码列表
    """
    for code in fund_codes:
        print(f"\n{'='*50}")
        print(f"开始处理基金 {code}")
        
        # 创建基金数据对象
        fund = FundData(code)
        
        # 获取净值数据
        data = fund.getNPV()
        
        # 保存数据到JSON文件
        if data:
            fund.save_to_json(data)
        
        # 每个基金处理完后暂停一下
        sleep(1)


if __name__ == '__main__':
    # 配置要采集的基金代码列表
    fund_codes = [
        '017516', 
        '270042',  
        '000628',
        '013172'
    ]
    
    # 开始采集数据
    collect_fund_data(fund_codes)
    
    print("\n所有基金数据处理完成")
