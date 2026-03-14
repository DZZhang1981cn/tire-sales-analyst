#!/usr/bin/env python3
"""
轮胎销售数据分析 - 数据库加载模块
提供从SQLite数据库加载数据的功能

使用方法:
    from database import load_data
    
    # 加载2026年1月销售数据
    sales_2026 = load_data('sales', month=202601)
    
    # 加载所有SNX数据
    snx_all = load_data('snx')
"""

import os
import sqlite3
import pandas as pd
from pathlib import Path

# 数据库路径
DB_PATH = os.path.expanduser("~/.openclaw/workspace/tire-analyst/skills/tire-sales-analyst/sales_analysis.db")

# 数据源路径（用于检查是否需要更新数据库）
BASE_PATH = os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs/共享/销售分析")


def check_and_update_database():
    """
    检查数据库是否需要更新，如果需要则自动更新
    
    Returns:
        bool: 数据库是否可用
    """
    import subprocess
    import glob
    
    # 获取数据库最后修改时间
    if not os.path.exists(DB_PATH):
        # 数据库不存在，需要构建
        print("📦 数据库不存在，正在构建...")
        subprocess.run(['python3', __file__.replace('database.py', 'build_database.py'), '--force'])
        return True
    
    # 获取数据源最新修改时间
    data_mtime = 0
    
    # 检查销售数据
    for f in glob.glob(f'{BASE_PATH}/Sales_rawdata/*.xlsx'):
        data_mtime = max(data_mtime, os.path.getmtime(f))
    
    # 检查SNX数据
    for f in glob.glob(f'{BASE_PATH}/SNX_rawdata/*.xlsx'):
        data_mtime = max(data_mtime, os.path.getmtime(f))
    
    # 检查价格数据
    for f in glob.glob(f'{BASE_PATH}/价格变化/*.xlsx'):
        data_mtime = max(data_mtime, os.path.getmtime(f))
    
    # 获取数据库修改时间
    db_mtime = os.path.getmtime(DB_PATH)
    
    # 如果数据源更新了，自动重建数据库
    if data_mtime > db_mtime:
        print("📦 数据源已更新，正在重建数据库...")
        subprocess.run(['python3', __file__.replace('database.py', 'build_database.py'), '--force'])
    
    return True


def get_connection():
    """获取数据库连接"""
    check_and_update_database()
    return sqlite3.connect(DB_PATH)


def load_data(table_name, month=None, year=None, **kwargs):
    """
    从数据库加载数据
    
    Args:
        table_name: 表名 (sales, snx, price, product_category, customer)
        month: 月份 (如 202601)
        year: 年份 (如 2025, 2026)
        **kwargs: 其他筛选条件
    
    Returns:
        DataFrame: 查询结果
    """
    conn = get_connection()
    
    try:
        # 验证表名
        valid_tables = ['sales', 'snx', 'price', 'product_category', 'customer']
        if table_name not in valid_tables:
            raise ValueError(f"无效的表名: {table_name}. 有效表: {valid_tables}")
        
        # 构建查询
        query = f"SELECT * FROM {table_name}"
        conditions = []
        
        if month:
            if table_name == 'sales' or table_name == 'snx':
                conditions.append(f"ID_Month_Key = '{month}'")
            elif table_name == 'price':
                conditions.append(f"价格_年月 = '{month}'")
        
        if year:
            if table_name == 'sales' or table_name == 'snx':
                conditions.append(f"数据年份 = {year}")
            elif table_name == 'price':
                conditions.append(f"价格_年份 = {year}")
        
        # 添加其他筛选条件
        for key, value in kwargs.items():
            if value is not None:
                if isinstance(value, str):
                    conditions.append(f"{key} = '{value}'")
                else:
                    conditions.append(f"{key} = {value}")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        df = pd.read_sql_query(query, conn)
        return df
        
    finally:
        conn.close()


def load_sales(month=None, year=None, channel=None, geobox=None, dealer_id=None):
    """
    加载销售数据
    
    Args:
        month: 月份 (如 202601)
        year: 年份 (如 2025, 2026)
        channel: 渠道分类 (如 '驰加', 'MLD')
        geobox: 规格 (如 '23550R18')
        dealer_id: 门店ID
    
    Returns:
        DataFrame: 销售数据
    """
    return load_data('sales', month=month, year=year, 
                     渠道分类=channel, Geobox=geobox, Dealer_ID=dealer_id)


def load_snx(month=None, year=None, channel=None, geobox=None, dealer_id=None):
    """
    加载SNX数据
    
    Args:
        month: 月份 (如 202601)
        year: 年份 (如 2025, 2026)
        channel: 渠道分类
        geobox: 规格
        dealer_id: 门店ID
    
    Returns:
        DataFrame: SNX数据
    """
    return load_data('snx', month=month, year=year,
                     渠道分类=channel, Geobox=geobox, Dealer_ID=dealer_id)


def load_price(month=None, year=None, cai=None):
    """
    加载价格数据
    
    Args:
        month: 月份 (如 202601)
        year: 年份 (如 2025, 2026)
        cai: CAI产品编码
    
    Returns:
        DataFrame: 价格数据
    """
    return load_data('price', month=month, year=year, CAI=cai)


def load_product_category(cai=None):
    """
    加载产品分类数据
    
    Args:
        cai: CAI产品编码
    
    Returns:
        DataFrame: 产品分类数据
    """
    return load_data('product_category', CAI=cai)


def load_customer(dealer_id=None, city=None):
    """
    加载客户名单
    
    Args:
        dealer_id: 门店ID
        city: 城市
    
    Returns:
        DataFrame: 客户名单
    """
    return load_data('customer', Dealer_ID=dealer_id, City=city)


def get_table_info():
    """获取数据库表信息"""
    conn = get_connection()
    cursor = conn.cursor()
    
    info = {}
    tables = ['sales', 'snx', 'price', 'product_category', 'customer']
    
    for table in tables:
        try:
            # 获取行数
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            
            # 获取列名
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [row[1] for row in cursor.fetchall()]
            
            info[table] = {
                'rows': count,
                'columns': columns
            }
        except Exception as e:
            info[table] = {'error': str(e)}
    
    conn.close()
    return info


# 便捷函数：加载分析所需的数据
def load_analysis_data(month_current, month_prev=None, month_yoy=None):
    """
    加载分析所需的标准数据组合
    
    Args:
        month_current: 当前月 (如 202601)
        month_prev: 上一月 (如 202512)
        month_yoy: 去年同期 (如 202501)
    
    Returns:
        dict: 包含 sales_current, snx_current, sales_prev, snx_prev, sales_yoy, snx_yoy 的字典
    """
    result = {}
    
    # 当前月数据
    result['sales_current'] = load_sales(month=month_current)
    result['snx_current'] = load_snx(month=month_current)
    
    # 上一月数据
    if month_prev:
        result['sales_prev'] = load_sales(month=month_prev)
        result['snx_prev'] = load_snx(month=month_prev)
    
    # 去年同期数据
    if month_yoy:
        result['sales_yoy'] = load_sales(month=month_yoy)
        result['snx_yoy'] = load_snx(month=month_yoy)
    
    return result


if __name__ == '__main__':
    # 测试数据库连接
    print("🛞 轮胎销售数据库连接测试")
    print("="*50)
    
    info = get_table_info()
    for table, data in info.items():
        print(f"\n📊 {table}:")
        if 'error' in data:
            print(f"   ❌ {data['error']}")
        else:
            print(f"   行数: {data['rows']:,}")
            print(f"   列: {', '.join(data['columns'][:5])}...")
    
    print("\n✅ 数据库连接正常")
