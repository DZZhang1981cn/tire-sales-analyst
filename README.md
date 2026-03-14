# tire-sales-analyst

轮胎销售数据分析技能 - 米其林浙江销售数据分析和报告生成工具

## 功能

- 18寸轮胎专题分析
- 渠道对比（销量vs SNX）
- Dealer表现分析
- 规格+CAI双重维度分析（含价格分析）
- 线上/线下购买行为分析
- 单一规格销量变化诊断分析
- 行业宏观数据获取（Tushare）
- Intelligence Hub行业报告复现

## 快速开始

```bash
# 安装依赖
pip install pandas openpyxl PyGithub

# 构建数据库
python build_database.py

# 运行分析
python database.py
```

## 数据来源

数据文件位于 `~/Library/Mobile Documents/com~apple~CloudDocs/共享/销售分析/`

## License

MIT
