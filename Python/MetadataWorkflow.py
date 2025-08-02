import os
import json
import time
import re
import requests
import logging
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def load_fund_codes():
    """从JSON文件加载基金代码列表"""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        code_path = os.path.join(base_dir, "../Fund/Meta/CnFundCode.json")
        
        with open(code_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # 检查数据结构并提取基金代码列表
            if isinstance(data, list):
                return data
            elif 'list' in data and isinstance(data['list'], list):
                return data['list']
            else:
                raise ValueError("CnFundCode.json 文件格式不符合预期")
    
    except Exception as e:
        logging.error(f"加载基金代码失败: {str(e)}")
        return []

def fetch_fund_html(fund_code):
    """获取基金HTML页面内容"""
    url = f"https://fundf10.eastmoney.com/jbgk_{fund_code}.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logging.error(f"获取基金 {fund_code} HTML 失败: {str(e)}")
        return None

def parse_fund_data(html, fund_code):
    """解析基金HTML数据"""
    soup = BeautifulSoup(html, 'html.parser')
    result = {"code": fund_code}
    
    # 解析基本信息表格
    info_table = soup.select_one('table.info.w790')
    if info_table:
        parse_basic_info(info_table, result)
    else:
        logging.warning(f"基金 {fund_code} 基本信息表格未找到")
    
    # 解析投资信息部分
    sections = soup.select('div.txt_cont div.box')
    if sections:
        parse_investment_info(sections, result)
    else:
        logging.warning(f"基金 {fund_code} 投资信息部分未找到")
    
    # 后处理：标准化字段名、格式化数据
    post_process_data(result)
    
    return result

def parse_basic_info(table, result):
    """解析基本信息表格"""
    for row in table.select('tr'):
        headers = row.select('th')
        cells = row.select('td')
        
        if not headers or not cells:
            continue
            
        # 处理一行一个键值对的情况
        if len(headers) == 1 and len(cells) >= 1:
            key = headers[0].get_text().strip()
            value_cell = cells[0]
            process_key_value(key, value_cell, result)
        
        # 处理一行两个键值对的情况
        elif len(headers) == 2 and len(cells) >= 2:
            key1 = headers[0].get_text().strip()
            value_cell1 = cells[0]
            key2 = headers[1].get_text().strip()
            value_cell2 = cells[1]
            
            process_key_value(key1, value_cell1, result)
            process_key_value(key2, value_cell2, result)

def process_key_value(key, value_cell, result):
    """处理键值对并存储到结果字典"""
    # 获取单元格文本内容（去除多余空白）
    text_value = ' '.join(value_cell.get_text().split()).strip()
    
    # 特殊处理资产规模字段
    if key == "资产规模":
        # 同时存储原始值用于后续处理
        result["资产规模原始值"] = text_value
    
    # 处理基金管理人（公司信息）
    elif key == "基金管理人":
        a_tag = value_cell.find('a')
        if a_tag:
            result["基金管理人"] = {
                "name": a_tag.get_text().strip(),
                "link": format_url(a_tag.get('href', ''))
            }
        else:
            result["基金管理人"] = {"name": text_value, "link": ""}
    
    # 处理基金托管人
    elif key == "基金托管人":
        a_tag = value_cell.find('a')
        if a_tag:
            result["基金托管人"] = {
                "name": a_tag.get_text().strip(),
                "link": format_url(a_tag.get('href', ''))
            }
        else:
            result["基金托管人"] = {"name": text_value, "link": ""}
    
    # 处理基金经理人（经理信息）
    elif key == "基金经理人":
        a_tag = value_cell.find('a')
        if a_tag:
            result["基金经理人"] = {
                "name": a_tag.get_text().strip(),
                "link": format_url(a_tag.get('href', ''))
            }
        else:
            result["基金经理人"] = {"name": text_value, "link": ""}
    
    # 处理其他标准字段
    elif key in ["基金简称", "基金全称", "基金类型", 
                "发行日期", "成立日期", "成立来分红",
                "管理费率", "托管费率", "销售服务费率",
                "最高认购费率", "最高申购费率", "最高赎回费率",
                "业绩比较基准", "跟踪标的"]:
        result[key] = text_value

def parse_investment_info(sections, result):
    """解析投资信息部分"""
    section_map = {
        "投资目标": "投资目标",
        "投资理念": "投资理念",
        "投资范围": "投资范围",
        "投资策略": "投资策略",
        "分红政策": "分红政策",
        "风险收益特征": "风险收益特征"
    }
    
    for section in sections:
        title_tag = section.find('h4', class_='t')
        if not title_tag:
            continue
            
        title = title_tag.get_text().strip()
        if title not in section_map:
            continue
            
        content_div = section.find('div', class_='boxitem')
        if content_div:
            # 清理多余空白和特殊字符
            content = content_div.get_text().strip()
            content = ' '.join(content.split())
            result[section_map[title]] = content

def format_url(url):
    """格式化URL"""
    if not url:
        return ""
    
    # 处理以//开头的URL
    if url.startswith("//"):
        return "https:" + url
    
    # 处理相对URL
    if url.startswith("/"):
        return "https://fund.eastmoney.com" + url
    
    return url

def extract_date(date_str):
    """
    从字符串中提取日期并转换为整数
    格式：YYYYMMDD
    """
    if not date_str:
        return 0
    
    # 尝试匹配常见日期格式：YYYY年MM月DD日
    match = re.search(r'(\d{4})[年\-](\d{1,2})[月\-](\d{1,2})', date_str)
    if match:
        year = match.group(1)
        month = match.group(2).zfill(2)
        day = match.group(3).zfill(2)
        try:
            return int(f"{year}{month}{day}")
        except ValueError:
            return 0
    
    return 0

def extract_size_info(size_str):
    """从规模字符串中提取数值和日期"""
    if not size_str:
        return None, 0
    
    # 提取规模数值
    size_value = ""
    size_match = re.search(r'([\d,.]+)\s*[亿万千]?[元份]?', size_str)
    if size_match:
        size_value = size_match.group(1).replace(',', '')
    
    # 提取截止日期
    size_date = extract_date(size_str)
    
    return size_value, size_date

def extract_dividend_info(dividend_str):
    """从分红字符串中提取分红信息"""
    if not dividend_str:
        return 0.0, 0
    
    # 提取每份分红金额
    amount = 0.0
    amount_match = re.search(r'每份累计([\d.]+)元', dividend_str)
    if amount_match:
        try:
            amount = float(amount_match.group(1))
        except ValueError:
            amount = 0.0
    
    # 提取分红次数
    times = 0
    times_match = re.search(r'(\d+)次', dividend_str)
    if times_match:
        try:
            times = int(times_match.group(1))
        except ValueError:
            times = 0
    
    return amount, times

def post_process_data(data):
    """后处理：标准化字段名、格式化数据"""
    # 字段名标准化
    field_mapping = {
        "基金简称": "name",
        "基金全称": "fund_name",
        "基金类型": "fund_type",
        "发行日期": "issue_date",
        "成立日期": "establish_date",
        "基金管理人": "fund_company",
        "基金托管人": "fund_custodian",
        "基金经理人": "fund_manager",
        "成立来分红": "dividend_info",
        "管理费率": "management_fee_rate",
        "托管费率": "custodian_fee_rate",
        "销售服务费率": "service_fee_rate",
        "最高认购费率": "max_subscription_fee_rate",
        "最高申购费率": "max_purchase_fee_rate",
        "最高赎回费率": "max_redemption_fee_rate",
        "业绩比较基准": "benchmark",
        "跟踪标的": "tracking_target",
        "投资目标": "investment_objective",
        "投资理念": "investment_philosophy",
        "投资范围": "investment_scope",
        "投资策略": "investment_strategy",
        "分红政策": "dividend_policy",
        "风险收益特征": "risk_return_characteristics"
    }
    
    # 重命名字段
    for old_key, new_key in field_mapping.items():
        if old_key in data:
            data[new_key] = data.pop(old_key)
    
    # 处理日期字段 - 转换为整数
    for date_field in ["issue_date", "establish_date"]:
        if date_field in data and isinstance(data[date_field], str):
            data[date_field] = extract_date(data[date_field])
    
    # 处理资产规模
    if "资产规模原始值" in data:
        size_value, size_date = extract_size_info(data["资产规模原始值"])
        if size_value:
            data["assets_size"] = size_value
            data["assets_size_date"] = size_date  # 已经是整数
        del data["资产规模原始值"]
    
    # 处理份额规模（如果存在）
    if "份额规模" in data:
        size_value, size_date = extract_size_info(data["份额规模"])
        if size_value:
            data["shares_size"] = size_value
            data["shares_size_date"] = size_date  # 已经是整数
        del data["份额规模"]
    
    # 处理分红信息
    if "dividend_info" in data:
        amount, times = extract_dividend_info(data["dividend_info"])
        data["dividend_per_share"] = amount
        data["dividend_times"] = times
        del data["dividend_info"]
    
    # 处理费率字段（保留数值部分）
    for fee_field in ["management_fee_rate", "custodian_fee_rate", "service_fee_rate",
                     "max_subscription_fee_rate", "max_purchase_fee_rate", "max_redemption_fee_rate"]:
        if fee_field in data:
            # 提取百分比数值（如 "1.20%" -> "1.20"）
            fee_match = re.search(r'([\d.]+)%', data[fee_field])
            if fee_match:
                data[fee_field] = fee_match.group(1)

def save_fund_metadata(fund_code, data):
    """保存基金元数据到JSON文件"""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(base_dir, "../Fund/Meta/CN/")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{fund_code}.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logging.info(f"成功保存基金 {fund_code} 元数据")
    except Exception as e:
        logging.error(f"保存基金 {fund_code} 元数据失败: {str(e)}")

def main():
    """主函数"""
    fund_codes = load_fund_codes()
    if not fund_codes:
        logging.error("没有找到基金代码，程序终止")
        return
    
    total = len(fund_codes)
    logging.info(f"开始采集 {total} 只基金数据...")
    
    for i, fund_code in enumerate(fund_codes, 1):
        logging.info(f"处理中 ({i}/{total}): {fund_code}")
        
        # 获取HTML内容
        html = fetch_fund_html(fund_code)
        if not html:
            logging.warning(f"跳过基金 {fund_code}，无法获取HTML内容")
            continue
        
        # 解析数据
        try:
            data = parse_fund_data(html, fund_code)
            if not data or len(data) <= 1:  # 只有code字段
                logging.warning(f"解析基金 {fund_code} 数据失败或数据不完整")
                continue
        except Exception as e:
            logging.error(f"解析基金 {fund_code} 数据时出错: {str(e)}")
            continue
        
        # 保存数据
        save_fund_metadata(fund_code, data)
        
        # 添加延迟避免请求过于频繁
        time.sleep(0.5)
    
    logging.info("所有基金数据采集完成！")

if __name__ == "__main__":
    main()
