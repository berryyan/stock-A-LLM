# test_databases.py
"""
股票分析系统 - 数据库集成测试
测试 MySQL 和 Milvus 的所有功能
"""

import sys
sys.path.append('.')

from database.mysql_connector import mysql_db
from database.milvus_connector import milvus_db
import numpy as np
import pandas as pd
from datetime import datetime

def test_mysql():
    """测试 MySQL 功能"""
    print("\n" + "=" * 70)
    print("MySQL 数据库测试")
    print("=" * 70)
    
    try:
        # 1. 测试连接
        print("\n1. 测试连接...")
        # 直接执行一个简单查询来测试连接
        try:
            test_result = mysql_db.execute_query("SELECT 1 as test")
            if len(test_result) > 0:
                print("   ✅ 连接成功")
            else:
                raise Exception("连接测试查询失败")
        except:
            raise Exception("连接失败")
        
        # 2. 获取股票列表
        print("\n2. 获取股票列表...")
        stocks = mysql_db.get_stock_list()
        print(f"   ✅ 找到 {len(stocks)} 只股票")
        print(f"   示例: {stocks['ts_code'].head(3).tolist()}")
        
        # 3. 测试日线数据
        test_stock = "000001.SZ"
        print(f"\n3. 获取 {test_stock} 的日线数据...")
        daily_data = mysql_db.get_stock_daily_data(test_stock, "20240601", "20240605")
        print(f"   ✅ 获取 {len(daily_data)} 条数据")
        if len(daily_data) > 0:
            print(f"   最新收盘价: {daily_data.iloc[-1]['close']}")
        
        # 4. 测试公告数据
        print(f"\n4. 获取 {test_stock} 的公告...")
        anns = mysql_db.get_company_announcements(test_stock, limit=3)
        print(f"   ✅ 获取 {len(anns)} 条公告")
        if len(anns) > 0:
            print(f"   最新公告: {anns.iloc[0]['title'][:30]}...")
        
        # 5. 测试问答数据
        print(f"\n5. 获取 {test_stock} 的投资者问答...")
        qa = mysql_db.get_qa_data(test_stock, limit=2)
        print(f"   ✅ 获取 {len(qa)} 条问答")
        
        # 6. 测试资金流向
        print(f"\n6. 获取 {test_stock} 的资金流向...")
        money_flow = mysql_db.get_money_flow(test_stock, "20240601", "20240605")
        print(f"   ✅ 获取 {len(money_flow)} 条数据")
        
        return True
        
    except Exception as e:
        print(f"\n❌ MySQL 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_milvus():
    """测试 Milvus 功能"""
    print("\n" + "=" * 70)
    print("Milvus 向量数据库测试")
    print("=" * 70)
    
    try:
        # 1. 连接
        print("\n1. 连接到 Milvus...")
        if not milvus_db.connect():
            raise Exception("连接失败")
        print("   ✅ 连接成功")
        
        # 2. 获取集合信息
        print("\n2. 获取集合信息...")
        stats = milvus_db.get_collection_stats()
        print(f"   ✅ 集合: {stats['name']}")
        print(f"   文档数: {stats['num_entities']}")
        
        # 3. 测试向量操作
        print("\n3. 测试向量操作...")
        
        # 准备测试文档
        test_doc = {
            "doc_id": f"test_integration_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "chunk_id": 1,
            "ts_code": "000001.SZ",
            "ann_date": "20240606",
            "title": "集成测试文档",
            "text": "这是一个用于集成测试的文档内容",
            "embedding": np.random.rand(1024).tolist(),
            "metadata": {"test": True, "timestamp": datetime.now().isoformat()}
        }
        
        # 插入
        ids = milvus_db.insert_documents([test_doc])
        print(f"   ✅ 插入文档 ID: {ids[0]}")
        
        # 搜索
        results = milvus_db.search(test_doc["embedding"], top_k=5)
        print(f"   ✅ 搜索到 {len(results)} 个结果")
        
        # 清理
        milvus_db.delete_by_expr(f"doc_id == '{test_doc['doc_id']}'")
        print("   ✅ 测试数据已清理")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Milvus 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        milvus_db.disconnect()

def main():
    """主函数"""
    print("\n🚀 股票分析系统 - 数据库集成测试")
    print("=" * 70)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 运行测试
    mysql_ok = test_mysql()
    milvus_ok = test_milvus()
    
    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    print(f"MySQL:  {'✅ 通过' if mysql_ok else '❌ 失败'}")
    print(f"Milvus: {'✅ 通过' if milvus_ok else '❌ 失败'}")
    
    if mysql_ok and milvus_ok:
        print("\n🎉 所有测试通过！系统已准备就绪。")
        print("\n下一步开发计划:")
        print("1. 实现文档处理模块 (rag/document_processor.py)")
        print("2. 集成嵌入模型 (models/embedding_model.py)")
        print("3. 实现 RAG Agent (agents/rag_agent.py)")
        print("4. 实现 SQL Agent (agents/sql_agent.py)")
        print("5. 创建混合 Agent (agents/hybrid_agent.py)")
        print("6. 开发 API 接口 (api/main.py)")
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息。")

if __name__ == "__main__":
    main()