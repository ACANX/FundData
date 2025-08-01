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
        self.data_file_path = None
    
    def get_data_file_path(self):
        """获取数据文件路径"""
        if not self.data_file_path:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            save_dir = os.path.join(current_dir, "..", "Fund", "Data", "CN")
            os.makedirs(save_dir, exist_ok=True)
            self.data_file_path = os.path.join(save_dir, f"{self.code}.json")
        return self.data_file_path
    
    def load_existing_data(self):
        """加载现有数据文件"""
        data_file = self.get_data_file_path()
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载基金 {self.code} 现有数据时出错: {str(e)}")
        return []
    
    def save_to_json(self, data):
        """
        将数据保存为JSON文件
        :param data: 要保存的数据
        :return: 文件保存路径
        """
        try:
            data_file = self.get_data_file_path()
            # 保存数据
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"基金 {self.code} 数据已保存到: {data_file}")
            
            return data_file
        except Exception as e:
            print(f"保存基金 {self.code} 数据时出错: {str(e)}")
            return None
    
    def get_first_page_data(self):
        """获取第一页数据（最新数据）"""
        try:
            page = 1
            url = "http://api.fund.eastmoney.com/f10/lsjz?callback=jQuery18304038998523093684_1586160530315"
            tempurl = url + "&fundCode={}&pageIndex={}&pageSize=20".format(self.code, page)
            header = {"Referer": "http://fundf10.eastmoney.com/jjjz_{}.html".format(self.code)}
            response = requests.get(tempurl, headers=header)
            response.raise_for_status()
            jsonData = response.content.decode()
            # 解析JSON数据
            dictData = json.loads(jsonData[41:-1])
            listDateData = dictData.get("Data", {"LSJZList": []}).get("LSJZList")
            dataList = []
            for item in listDateData:
                # 获取日期并去除横线 (yyyy-MM-dd -> yyyyMMdd)
                rawDate = item.get("FSRQ", "")
                npvDate = rawDate.replace("-", "") if rawDate else ""
                npv = item.get("DWJZ")
                tempRate = item.get("JZZZL")
                rate = "0.00" if tempRate == "" else tempRate
                dataList.append({
                    "date": npvDate,
                    "nav": npv,
                    "change_rate": rate
                })
            
            return dataList
        except Exception as e:
            print(f"基金 {self.code} 获取第一页数据失败: {str(e)}")
            return []

    def getNPV(self, incremental=False):
        """
        查询净值数据
        :param incremental: 是否增量采集（只获取最新数据）
        :return: 净值数据列表
        """
        try:
            if incremental:
                print(f"基金 {self.code} 执行增量采集")
                # 只获取第一页数据（最新数据）
                return self.get_first_page_data()
            
            print(f"基金 {self.code} 执行全量采集")
            page = 1
            url = "http://api.fund.eastmoney.com/f10/lsjz?callback=jQuery18304038998523093684_1586160530315"
            tempurl = url + "&fundCode={}&pageIndex={}&pageSize=20".format(self.code, page)
            header = {"Referer": "http://fundf10.eastmoney.com/jjjz_{}.html".format(self.code)}

            # 发送初始请求获取总页数
            response = requests.get(tempurl, headers=header)
            response.raise_for_status()
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
                # 获取日期并去除横线 (yyyy-MM-dd -> yyyyMMdd)
                rawDate = item.get("FSRQ", "")
                npvDate = rawDate.replace("-", "") if rawDate else ""
                npv = item.get("DWJZ")
                tempRate = item.get("JZZZL")
                rate = "0.00" if tempRate == "" else tempRate
                dataList.append({
                    "date": npvDate,
                    "nav": npv,
                    "change_rate": rate
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
                        # 获取日期并去除横线 (yyyy-MM-dd -> yyyyMMdd)
                        rawDate = item.get("FSRQ", "")
                        npvDate = rawDate.replace("-", "") if rawDate else ""
                        npv = item.get("DWJZ")
                        tempRate = item.get("JZZZL")
                        rate = "0.00" if tempRate == "" else tempRate
                        dataList.append({
                            "date": npvDate,
                            "nav": npv,
                            "change_rate": rate
                        })
                    sleep(1.5)
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


def merge_data(existing_data, new_data):
    """
    合并新旧数据，确保不重复
    :param existing_data: 现有数据
    :param new_data: 新采集的数据
    :return: 合并后的数据
    """
    # 创建日期映射的字典
    date_map = {item['date']: item for item in existing_data}
    # 添加新数据，覆盖旧数据（如果日期相同）
    for item in new_data:
        date_map[item['date']] = item
    # 转换为列表并按日期倒序排序
    merged_data = list(date_map.values())
    merged_data.sort(key=lambda x: x['date'], reverse=True)
    return merged_data

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
        # 检查数据文件是否存在
        data_file = fund.get_data_file_path()
        existing_data = fund.load_existing_data()
        # 决定采集策略
        if existing_data and len(existing_data) >= 20:
            # 增量采集 - 只获取最新数据
            print(f"基金 {code} 采用增量采集模式")
            new_data = fund.getNPV(incremental=True)
            # 合并新旧数据
            merged_data = merge_data(existing_data, new_data)
            print(f"基金 {code} 合并数据: 原有 {len(existing_data)} 条 + 新增 {len(new_data)} 条 = 合并后 {len(merged_data)} 条")
            # 保存合并后的数据
            fund.save_to_json(merged_data)
        else:
            # 全量采集
            print(f"基金 {code} 采用全量采集模式")
            data = fund.getNPV()
            if data:
                fund.save_to_json(data)
        # 每个基金处理完后暂停一下
        sleep(1)

def load_fund_codes_from_file():
    """
    从JSON文件加载基金代码列表
    :return: 基金代码列表
    """
    try:
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))        
        # 构建Meta文件路径
        meta_file = os.path.join(current_dir, "..", "Fund", "Meta", "CnFundCode.json")
        # 检查文件是否存在
        if not os.path.exists(meta_file):
            print(f"错误: 基金代码配置文件不存在 - {meta_file}")
            return []
        # 读取JSON文件
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta_data = json.load(f)
        # 获取基金代码列表
        fund_codes = meta_data.get("list", [])
        print(f"从配置文件加载了 {len(fund_codes)} 个基金代码")
        return fund_codes
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {str(e)}")
        return []
    except Exception as e:
        print(f"加载基金代码时出错: {str(e)}")
        return []


if __name__ == '__main__':
    # 从配置文件加载基金代码列表
    fund_codes = load_fund_codes_from_file()    
    # 开始采集数据
    collect_fund_data(fund_codes)
    print("\n所有基金数据处理完成")
