import os
import json
import time
import requests
from bs4 import BeautifulSoup

# 读取基金代码列表
def load_fund_codes():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    code_path = os.path.join(base_dir, "../Fund/Meta/CnFundCode.json")
    
    with open(code_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 采集基金元数据
def fetch_fund_metadata(fund_code):
    url = f"https://fundf10.eastmoney.com/jbgk_{fund_code}.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return parse_fund_data(response.text, fund_code)
    except Exception as e:
        print(f"采集失败 {fund_code}: {str(e)}")
        return None

# 解析基金数据
def parse_fund_data(html, fund_code):
    soup = BeautifulSoup(html, 'html.parser')
    result = {"基金代码": fund_code}
    
    # 解析基本信息表格
    info_tables = soup.select('div.info')
    if info_tables:
        parse_basic_info(info_tables[0], result)
    
    # 解析费率信息
    if len(info_tables) > 1:
        parse_fee_info(info_tables[1], result)
    
    # 解析投资信息
    sections = soup.select('div.txt_cont')
    parse_investment_info(sections, result)
    
    return result

def parse_basic_info(table, result):
    for row in table.select('tr'):
        cells = row.select('td')
        if len(cells) < 2:
            continue
            
        key = cells[0].get_text().strip()
        value = cells[1].get_text().strip()
        
        # 特殊处理资产规模字段
        if key == "资产规模":
            if '/' in value:
                assets, shares = value.split('/', 1)
                result["资产规模"] = assets.strip()
                result["份额规模"] = shares.strip()
            else:
                result["资产规模"] = value
        # 处理其他标准字段
        elif key in ["基金全称", "基金简称", "基金类型", 
                    "发行日期", "成立日期", "基金管理人", 
                    "基金托管人", "基金经理人", "成立来分红",
                    "业绩比较基准", "跟踪标的"]:
            result[key] = value

def parse_fee_info(table, result):
    for row in table.select('tr'):
        cells = row.select('td')
        if len(cells) < 2:
            continue
            
        key = cells[0].get_text().strip()
        value = cells[1].get_text().strip()
        
        if key in ["管理费率", "托管费率", "销售服务费率", 
                  "最高认购费率", "最高申购费率", "最高赎回费率"]:
            result[key] = value

def parse_investment_info(sections, result):
    section_map = {
        "投资目标": "投资目标",
        "投资理念": "投资理念",
        "投资范围": "投资范围",
        "投资策略": "投资策略",
        "分红政策": "分红政策",
        "风险收益特征": "风险收益特征"
    }
    
    for section in sections:
        title_tag = section.find('h4')
        if not title_tag:
            continue
            
        title = title_tag.get_text().strip()
        if title not in section_map:
            continue
            
        content_div = section.find('div', class_='txt_inner')
        if content_div:
            # 清理多余空白和特殊字符
            content = ' '.join(content_div.get_text().split())
            result[section_map[title]] = content

# 保存结果到文件
def save_fund_metadata(fund_code, data):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "../Fund/Meta/CN/")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{fund_code}.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 主程序
def main():
    fund_codes = load_fund_codes()
    total = len(fund_codes)
    print(f"开始采集 {total} 只基金数据...")
    for i, fund_code in enumerate(fund_codes, 1):
        print(f"处理中 ({i}/{total}): {fund_code}")
        data = fetch_fund_metadata(fund_code)
        if data:
            save_fund_metadata(fund_code, data)
        # 添加延迟避免请求过于频繁
        time.sleep(0.5)
    print("所有基金数据采集完成！")

if __name__ == "__main__":
    main()

