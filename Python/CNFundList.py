import os
import json
import glob
from datetime import datetime

# 配置路径
current_dir = os.path.dirname(os.path.abspath(__file__))
meta_dir = os.path.join(current_dir, '../Fund/Meta/CN/')
output_file = os.path.join(current_dir, '../Fund/README.md')

def extract_fund_data(json_file):
    """从JSON文件中提取基金数据"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"错误读取文件 {json_file}: {e}")
        return None
    
    # 提取基本字段
    code = data.get('code', 'N/A')
    name = data.get('name', 'N/A')
    fund_type = data.get('fund_type', 'N/A')
    
    # 处理成立日期格式
    issue_date = data.get('issue_date', 'N/A')
    if issue_date != 'N/A':
        try:
            # 尝试解析日期并格式化为YYYY-MM-DD
            date_obj = datetime.strptime(issue_date, '%Y-%m-%d')
            issue_date = date_obj.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            # 保留原始值
            pass
    
    link = data.get('link', '#')
    
    # 提取基金公司信息
    company = data.get('fund_company', {})
    company_name = company.get('name', 'N/A')
    company_link = company.get('link', '#')    
    # 提取基金经理信息
    manager = data.get('fund_manager', [])

    nav = data.get('nav', 'N/A')
    nav_date = data.get('nav_date', 'N/A')
    nage_change_rate = data.get('nage_change_rate', 'N/A')

    # 资产规模信息
    assets_size = data.get('assets_size', 'N/A')
    assets_size_date = data.get('assets_size_date', 'N/A')
    
    return {
        'code': code,
        'name': name,
        'fund_type': fund_type,
        'issue_date': issue_date,
        'link': link,
        'company_name': company_name,
        'company_link': company_link,
        'manager': manager,
        'nav': nav,
        'nav_date': nav_date,
        'nage_change_rate': nage_change_rate,
        'assets_size': assets_size,
        'assets_size_date': assets_size_date
    }

def generateManagerLinkText(arr):
    text = ""
    for manager in arr:
        manager_name = manager.get('name', 'N/A')
        manager_link = manager.get('link', '#')
        text += f"[{manager_name}]({manager_link})、" if manager_link != '#' else manager_name
    # 移除末尾多余的顿号
    if text.endswith('、'):
        text = text[:-1]  # 删除最后一个字符（顿号）
    return text

def generate_markdown_table(funds_data):
    """生成Markdown表格"""
    # 表格标题行
    table = "| 基金代码 | 基金名称 |  基金公司 | 基金经理 | 基金类型 | 成立日期 | 资产规模(亿元) |报告日期| 最新净值|\n"
    table += "|----------|----------|----------|----------|----------|----------|----------|----------|----------|\n"
    
    # 按基金代码排序
    sorted_funds = sorted(funds_data, key=lambda x: x['code'])
    
    for fund in sorted_funds:
        # 创建带链接的基金代码
        code_link = f"[{fund['code']}]({fund['link']})" if fund['link'] != '#' else fund['code']
        # 带链接的基金名称
        name_link = f"[{fund['name']}](/Fund/Meta/CN/{fund['code']}.json)"
        # 创建带链接的基金公司
        company_link = f"[{fund['company_name']}]({fund['company_link']})" if fund['company_link'] != '#' else fund['company_name']
        # 创建带链接的基金经理
        manager_link = generateManagerLinkText(fund['manager'])
        # 带链接的最新净值
        nav_link = f"[{fund['nav']}({fund['nage_change_rate']}%)](https://fund.eastmoney.com/{fund['code']}.html)"
        # 添加表格行
        table += f"| {code_link} | {name_link} |{company_link} | {manager_link} | {fund['fund_type']} | {fund['issue_date']} | {fund['assets_size']} | {fund['assets_size_date']} | {nav_link} |\n"
    return table

def main():
    # 确保元数据目录存在
    if not os.path.exists(meta_dir):
        print(f"错误: 元数据目录不存在 - {meta_dir}")
        return
    # 查找所有JSON文件
    json_files = glob.glob(os.path.join(meta_dir, '*.json'))
    if not json_files:
        print(f"警告: 在 {meta_dir} 中没有找到JSON文件")
        return
    funds_data = []
    for json_file in json_files:
        fund_data = extract_fund_data(json_file)
        if fund_data:
            funds_data.append(fund_data)
    # 生成Markdown内容
    markdown_content = f"# 基金列表\n\n"
    markdown_content += "   \n\n"
    markdown_content += generate_markdown_table(funds_data)
    markdown_content += f"- 最后更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    markdown_content += f"- 共包含基金数量: {len(funds_data)}\n\n"
    # 写入README文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"成功生成基金列表: {output_file}")
        print(f"处理基金数量: {len(funds_data)}")
    except Exception as e:
        print(f"写入文件失败: {e}")

if __name__ == "__main__":
    main()
