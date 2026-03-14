#!/usr/bin/env python3
"""
轮胎销售数据分析 - 数据库构建/更新脚本
将所有数据文件整合到一个SQLite数据库中，加快分析效率

使用方法:
    python3 build_database.py          # 更新数据库
    python3 build_database.py --force   # 强制重建
    python3 build_database.py --check   # 仅检查是否需要更新
"""

import os
import sys
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
import argparse
import glob

# 数据库路径
DB_PATH = os.path.expanduser("~/.openclaw/workspace/tire-analyst/skills/tire-sales-analyst/sales_analysis.db")

# 数据源路径
BASE_PATH = os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs/共享/销售分析")

# 数据文件配置
DATA_FILES = {
    # 销售数据
    'sales_2025': f'{BASE_PATH}/Sales_rawdata/2025_sales.xlsx',
    'sales_2026': f'{BASE_PATH}/Sales_rawdata/2026_sales.xlsx',
    # SNX数据
    'snx_2025': f'{BASE_PATH}/SNX_rawdata/2025_SNX.xlsx',
    'snx_2026': f'{BASE_PATH}/SNX_rawdata/2026_SNX.xlsx',
    # 产品分类
    'product_category': f'{BASE_PATH}/产品清单/Product Category_V75_20260129.xlsx',
    # 客户名单（最新）
    'customer_latest': f'{BASE_PATH}/分月客户信息/2026客户名单.xlsx',
}

# 价格文件（动态获取）
def get_price_files():
    """获取所有价格文件"""
    price_dir = f'{BASE_PATH}/价格变化'
    files = glob.glob(f'{price_dir}/????????价格.xlsx')
    return sorted(files)


def get_file_mtime(filepath):
    """获取文件最后修改时间"""
    if os.path.exists(filepath):
        return os.path.getmtime(filepath)
    return 0


def get_latest_mtime():
    """获取所有数据文件的最新修改时间"""
    mtimes = []
    
    # 销售和SNX文件
    for key, path in DATA_FILES.items():
        if isinstance(path, str) and os.path.exists(path):
            mtimes.append(get_file_mtime(path))
    
    # 价格文件
    for path in get_price_files():
        mtimes.append(get_file_mtime(path))
    
    return max(mtimes) if mtimes else 0


def needs_update():
    """检查数据库是否需要更新"""
    if not os.path.exists(DB_PATH):
        return True
    
    db_mtime = get_file_mtime(DB_PATH)
    data_mtime = get_latest_mtime()
    
    return data_mtime > db_mtime


def init_database():
    """初始化数据库连接"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn


def load_sales_data(conn):
    """加载销售数据"""
    print("📊 加载销售数据...")
    
    dfs = []
    
    # 加载2025年数据
    if os.path.exists(DATA_FILES['sales_2025']):
        df = pd.read_excel(DATA_FILES['sales_2025'])
        df['数据年份'] = 2025
        dfs.append(df)
        print(f"   - 2025年销售数据: {len(df):,} 行")
    
    # 加载2026年数据
    if os.path.exists(DATA_FILES['sales_2026']):
        df = pd.read_excel(DATA_FILES['sales_2026'])
        df['数据年份'] = 2026
        dfs.append(df)
        print(f"   - 2026年销售数据: {len(df):,} 行")
    
    if dfs:
        # 合并数据
        sales = pd.concat(dfs, ignore_index=True)
        
        # 添加规格字段（Geobox）
        def extract_geobox(text):
            if pd.isna(text):
                return ''
            text = str(text).upper().replace('/', ' ').replace('-', ' ')
            match = re.search(r'(\d{3})\s*(\d{2})\s*R\s*(\d{2})', text)
            if match:
                return f"{match.group(1)}{match.group(2)}R{match.group(3)}"
            return ''
        
        import re
        sales['Geobox'] = sales['Product_Description'].apply(extract_geobox)
        
        # 添加渠道分类
        def classify_channel(program_type):
            if pd.isna(program_type):
                return '未知'
            pt = str(program_type).upper()
            if 'TYREPLUS' in pt:
                return '驰加'
            elif 'MCR' in pt or 'MAR' in pt:
                return '非驰加零售'
            elif 'MLD' in pt:
                return 'MLD'
            elif 'FDD' in pt:
                return 'FDD'
            elif 'MPC' in pt or 'BOC' in pt:
                return '批发'
            else:
                return '其他'
        
        sales['渠道分类'] = sales['Program_Type'].apply(classify_channel)
        
        # 保存到数据库
        sales.to_sql('sales', conn, if_exists='replace', index=False)
        print(f"   ✅ 销售数据已保存: {len(sales):,} 行")
        
        return len(sales)
    return 0


def load_snx_data(conn):
    """加载SNX数据"""
    print("🔍 加载SNX数据...")
    
    dfs = []
    
    # 加载2025年数据
    if os.path.exists(DATA_FILES['snx_2025']):
        df = pd.read_excel(DATA_FILES['snx_2025'])
        df['数据年份'] = 2025
        dfs.append(df)
        print(f"   - 2025年SNX数据: {len(df):,} 行")
    
    # 加载2026年数据
    if os.path.exists(DATA_FILES['snx_2026']):
        df = pd.read_excel(DATA_FILES['snx_2026'])
        df['数据年份'] = 2026
        dfs.append(df)
        print(f"   - 2026年SNX数据: {len(df):,} 行")
    
    if dfs:
        snx = pd.concat(dfs, ignore_index=True)
        
        # 添加规格字段
        def extract_geobox(text):
            if pd.isna(text):
                return ''
            text = str(text).upper().replace('/', ' ').replace('-', ' ')
            match = re.search(r'(\d{3})\s*(\d{2})\s*R\s*(\d{2})', text)
            if match:
                return f"{match.group(1)}{match.group(2)}R{match.group(3)}"
            return ''
        
        import re
        snx['Geobox'] = snx['Product_Description'].apply(extract_geobox)
        
        # 添加渠道分类
        def classify_channel(program_type):
            if pd.isna(program_type):
                return '未知'
            pt = str(program_type).upper()
            if 'TYREPLUS' in pt:
                return '驰加'
            elif 'MCR' in pt or 'MAR' in pt:
                return '非驰加零售'
            elif 'MLD' in pt:
                return 'MLD'
            elif 'FDD' in pt:
                return 'FDD'
            elif 'MPC' in pt or 'BOC' in pt:
                return '批发'
            else:
                return '其他'
        
        snx['渠道分类'] = snx['Program_Type'].apply(classify_channel)
        
        # 保存到数据库
        snx.to_sql('snx', conn, if_exists='replace', index=False)
        print(f"   ✅ SNX数据已保存: {len(snx):,} 行")
        
        return len(snx)
    return 0


def load_price_data(conn):
    """加载价格数据"""
    import re
    print("💰 加载价格数据...")
    
    price_files = get_price_files()
    
    dfs = []
    for pf in price_files:
        # 从文件名提取年月
        filename = os.path.basename(pf)
        # 格式: 20250101价格.xlsx 或 20260301价格.xlsx
        date_match = re.search(r'(\d{4})(\d{2})\d{2}价格', filename)
        if date_match:
            year = int(date_match.group(1))
            month = int(date_match.group(2))
            period = year * 100 + month
            
            df = pd.read_excel(pf)
            df['价格_年月'] = period
            df['价格_年份'] = year
            df['价格_月份'] = month
            dfs.append(df)
            print(f"   - {year}年{month:02d}月价格数据: {len(df)} 行")
    
    if dfs:
        price = pd.concat(dfs, ignore_index=True)
        
        # 标准化列名
        # 查找CAI列
        cai_cols = [c for c in price.columns if 'CAI' in c.upper()]
        if cai_cols:
            price = price.rename(columns={cai_cols[0]: 'CAI'})
        
        # 查找底价列
        price_cols = [c for c in price.columns if '底价' in c or 'RTM' in c]
        if price_cols:
            price = price.rename(columns={price_cols[0]: '底价'})
        
        # 保存到数据库
        price.to_sql('price', conn, if_exists='replace', index=False)
        print(f"   ✅ 价格数据已保存: {len(price):,} 行")
        
        return len(price)
    return 0


def load_product_category(conn):
    """加载产品分类数据"""
    print("📦 加载产品分类...")
    
    if os.path.exists(DATA_FILES['product_category']):
        df = pd.read_excel(DATA_FILES['product_category'])
        df.to_sql('product_category', conn, if_exists='replace', index=False)
        print(f"   ✅ 产品分类已保存: {len(df):,} 行")
        return len(df)
    return 0


def load_customer_data(conn):
    """加载客户名单"""
    print("🏪 加载客户名单...")
    
    if os.path.exists(DATA_FILES['customer_latest']):
        df = pd.read_excel(DATA_FILES['customer_latest'])
        
        # 查找门店ID列（通常是第1列）
        # 重命名为标准名称
        cols = df.columns.tolist()
        if cols:
            # 假设第1列是Dealer_ID
            df = df.rename(columns={cols[0]: 'Dealer_ID'})
        
        df.to_sql('customer', conn, if_exists='replace', index=False)
        print(f"   ✅ 客户名单已保存: {len(df):,} 行")
        return len(df)
    return 0


def create_indexes(conn):
    """创建索引以加快查询"""
    print("🔧 创建索引...")
    
    indexes = [
        # 销售表索引
        "CREATE INDEX IF NOT EXISTS idx_sales_month ON sales(ID_Month_Key)",
        "CREATE INDEX IF NOT EXISTS idx_sales_dealer ON sales(Dealer_ID)",
        "CREATE INDEX IF NOT EXISTS idx_sales_cai ON sales(Cai)",
        "CREATE INDEX IF NOT EXISTS idx_sales_geobox ON sales(Geobox)",
        "CREATE INDEX IF NOT EXISTS idx_sales_program ON sales(Program_Type)",
        "CREATE INDEX IF NOT EXISTS idx_sales_channel ON sales(渠道分类)",
        
        # SNX表索引
        "CREATE INDEX IF NOT EXISTS idx_snx_month ON snx(ID_Month_Key)",
        "CREATE INDEX IF NOT EXISTS idx_snx_dealer ON snx(Dealer_ID)",
        "CREATE INDEX IF NOT EXISTS idx_snx_cai ON snx(Product_Description)",
        "CREATE INDEX IF NOT EXISTS idx_snx_geobox ON snx(Geobox)",
        "CREATE INDEX IF NOT EXISTS idx_snx_program ON snx(Program_Type)",
        
        # 价格表索引
        "CREATE INDEX IF NOT EXISTS idx_price_cai ON price(CAI)",
        "CREATE INDEX IF NOT EXISTS idx_price_period ON price(价格_年月)",
        
        # 客户表索引
        "CREATE INDEX IF NOT EXISTS idx_customer_dealer ON customer(Dealer_ID)",
        
        # 产品分类索引
        "CREATE INDEX IF NOT EXISTS idx_product_cai ON product_category(CAI)",
    ]
    
    for idx_sql in indexes:
        try:
            conn.execute(idx_sql)
        except Exception as e:
            print(f"   ⚠️ 索引创建警告: {e}")
    
    conn.commit()
    print("   ✅ 索引创建完成")


def save_metadata(conn):
    """保存数据库元数据"""
    import re
    
    cursor = conn.cursor()
    
    # 获取各表记录数
    tables = ['sales', 'snx', 'price', 'product_category', 'customer']
    stats = {}
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = cursor.fetchone()[0]
        except:
            stats[table] = 0
    
    # 保存元数据
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS db_metadata (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TEXT
        )
    """)
    
    cursor.execute("""
        INSERT OR REPLACE INTO db_metadata (key, value, updated_at)
        VALUES (?, ?, ?)
    """, ('last_update', datetime.now().isoformat(), datetime.now().isoformat()))
    
    for table, count in stats.items():
        cursor.execute("""
            INSERT OR REPLACE INTO db_metadata (key, value, updated_at)
            VALUES (?, ?, ?)
        """, (f'{table}_count', str(count), datetime.now().isoformat()))
    
    conn.commit()
    return stats


def build_database(force=False):
    """构建/更新数据库"""
    import re
    
    print("\n" + "="*50)
    print("🛞 轮胎销售数据库构建")
    print("="*50)
    
    # 检查是否需要更新
    if not force and not needs_update():
        print("✅ 数据库已是最新，无需更新")
        print(f"   数据库位置: {DB_PATH}")
        return True
    
    # 创建数据库连接
    conn = init_database()
    
    try:
        # 加载各类数据
        sales_count = load_sales_data(conn)
        snx_count = load_snx_data(conn)
        price_count = load_price_data(conn)
        product_count = load_product_category(conn)
        customer_count = load_customer_data(conn)
        
        # 创建索引
        create_indexes(conn)
        
        # 保存元数据
        stats = save_metadata(conn)
        
        print("\n" + "="*50)
        print("✅ 数据库构建完成!")
        print("="*50)
        print(f"📁 数据库位置: {DB_PATH}")
        print(f"📊 数据统计:")
        print(f"   - 销售数据: {stats.get('sales', 0):,} 行")
        print(f"   - SNX数据: {stats.get('snx', 0):,} 行")
        print(f"   - 价格数据: {stats.get('price', 0):,} 行")
        print(f"   - 产品分类: {stats.get('product_category', 0):,} 行")
        print(f"   - 客户名单: {stats.get('customer', 0):,} 行")
        print(f"   - 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ 数据库构建失败: {e}")
        raise
    finally:
        conn.close()
    
    return True


def check_database():
    """检查数据库状态"""
    print("\n" + "="*50)
    print("🔍 数据库状态检查")
    print("="*50)
    
    if not os.path.exists(DB_PATH):
        print("❌ 数据库不存在，需要构建")
        return False
    
    # 获取数据库信息
    db_mtime = datetime.fromtimestamp(get_file_mtime(DB_PATH))
    data_mtime = datetime.fromtimestamp(get_latest_mtime())
    
    print(f"📁 数据库位置: {DB_PATH}")
    print(f"   数据库更新时间: {db_mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   数据源最新时间: {data_mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if needs_update():
        print("⚠️ 数据库需要更新")
        return False
    else:
        print("✅ 数据库已是最新")
    
    # 显示数据统计
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        tables = ['sales', 'snx', 'price', 'product_category', 'customer']
        print(f"\n📊 数据统计:")
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   - {table}: {count:,} 行")
            except:
                print(f"   - {table}: 0 行")
        
        conn.close()
    except Exception as e:
        print(f"⚠️ 无法读取数据库统计: {e}")
    
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='轮胎销售数据库构建工具')
    parser.add_argument('--force', '-f', action='store_true', help='强制重建数据库')
    parser.add_argument('--check', '-c', action='store_true', help='仅检查数据库状态')
    
    args = parser.parse_args()
    
    if args.check:
        check_database()
    elif args.force or args.check:
        build_database(force=args.force)
    else:
        build_database()
