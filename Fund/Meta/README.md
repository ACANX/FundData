### 基金元数据字段映射表

| 原始字段名 | 处理后字段名 | 类型 | 说明 |
|------------|--------------|------|------|
| 基金代码 | code | string | 基金唯一代码 |
| 基金全称 | fund_name | string | 基金法定全名 |
| 基金简称 | name | string | 基金常用简称 |
| 基金类型 | fund_type | string | 基金类型分类（如股票型、混合型等） |
| 发行日期 | issue_date | string(8) | 基金发行日期（格式：YYYYMMDD） |
| 成立日期 | establish_date | string(8) | 基金成立日期（格式：YYYYMMDD） |
| 基金管理人 | fund_manager | object | 基金管理公司信息（包含名称和链接） |
| 基金托管人 | fund_custodian | object | 基金托管银行信息（包含名称和链接） |
| 基金经理人 | fund_manager_person | object | 基金经理信息（包含名称和链接） |
| 成立来分红 | dividend_per_share<br>dividend_times | float<br>integer | 每份累计分红金额<br>分红次数 |
| 管理费率 | management_fee_rate | string | 基金管理费率（百分比数值） |
| 托管费率 | custodian_fee_rate | string | 基金托管费率（百分比数值） |
| 销售服务费率 | service_fee_rate | string | 基金销售服务费率（百分比数值） |
| 最高认购费率 | max_subscription_fee_rate | string | 最高认购费率（百分比数值） |
| 最高申购费率 | max_purchase_fee_rate | string | 最高申购费率（百分比数值） |
| 最高赎回费率 | max_redemption_fee_rate | string | 最高赎回费率（百分比数值） |
| 业绩比较基准 | benchmark | string | 基金业绩比较基准 |
| 跟踪标的 | tracking_target | string | 基金跟踪的标的指数 |
| 资产规模 | assets_size | string | 基金资产规模（纯数值） |
| 资产规模截止日期 | assets_size_date | string(8) | 资产规模更新日期（格式：YYYYMMDD） |
| 份额规模 | shares_size | string | 基金份额规模（纯数值） |
| 份额规模截止日期 | shares_size_date | string(8) | 份额规模更新日期（格式：YYYYMMDD） |
| 投资目标 | investment_objective | string | 基金投资目标描述 |
| 投资理念 | investment_philosophy | string | 基金投资理念描述 |
| 投资范围 | investment_scope | string | 基金投资范围描述 |
| 投资策略 | investment_strategy | string | 基金投资策略描述 |
| 分红政策 | dividend_policy | string | 基金分红政策描述 |
| 风险收益特征 | risk_return_characteristics | string | 基金风险收益特征描述 |


### 字段说明

1. **对象类型字段**：
   - `fund_manager`：包含`name`（名称）和`link`（链接）
   - `fund_custodian`：包含`name`（名称）和`link`（链接）
   - `fund_manager_person`：包含`name`（名称）和`link`（链接）

2. **日期格式**：
   - 所有日期字段均转换为8位数字格式：YYYYMMDD
   - 例如："2025年06月30日" → "20250630"

3. **规模字段**：
   - `assets_size`：纯数值（如"123.40"）
   - `shares_size`：纯数值（如"25.9022"）
   - 对应的`*_date`字段记录数据更新日期

4. **费率字段**：
   - 保留百分比数值部分（如"1.20%" → "1.20"）
   - 未进行百分比转换，保持原始数值

5. **分红字段**：
   - `dividend_per_share`：每份累计分红金额
   - `dividend_times`：分红总次数
