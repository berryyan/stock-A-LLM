#!/usr/bin/env python3
"""
诊断智能日期解析对RAG查询的干预问题
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from utils.date_intelligence import date_intelligence
    print("✅ 智能日期解析模块加载成功")
except Exception as e:
    print(f"❌ 智能日期解析模块加载失败: {e}")
    exit(1)

def test_date_intelligence_intervention():
    """测试智能日期解析对RAG查询的干预"""
    print("\n🔍 测试智能日期解析对RAG查询的干预")
    print("=" * 60)
    
    test_questions = [
        "贵州茅台2024年的经营策略",
        "茅台最新公告说了什么", 
        "平安银行的经营风险",
        "贵州茅台的主营业务是什么"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n测试 {i}: {question}")
        print("-" * 40)
        
        try:
            # 调用智能日期解析
            processed_question, parsing_result = date_intelligence.preprocess_question(question)
            
            print(f"原问题: {question}")
            print(f"处理后问题: {processed_question}")
            print(f"解析结果:")
            
            for key, value in parsing_result.items():
                if value is not None:
                    print(f"  - {key}: {value}")
            
            # 检查是否有不必要的修改
            if question != processed_question:
                print("⚠️  问题被修改了！")
            
            # 检查是否添加了时间过滤
            if parsing_result.get('date_type') or parsing_result.get('parsed_date'):
                print("⚠️  添加了时间过滤条件！")
                
            # 检查股票代码解析
            if parsing_result.get('stock_code'):
                print(f"✅ 股票代码解析: {parsing_result['stock_code']}")
                
        except Exception as e:
            print(f"❌ 解析失败: {e}")
            import traceback
            traceback.print_exc()

def check_milvus_data():
    """检查Milvus中的实际数据"""
    print("\n🔍 检查Milvus中的实际数据")
    print("=" * 60)
    
    try:
        from database.milvus_connector import MilvusConnector
        
        milvus = MilvusConnector()
        
        # 检查集合是否存在和加载状态
        if hasattr(milvus, 'collection') and milvus.collection:
            print(f"✅ 集合已连接: {milvus.collection.name}")
            
            # 检查数据数量
            try:
                milvus.collection.load()
                count = milvus.collection.num_entities
                print(f"✅ 数据总量: {count:,} 条")
            except Exception as e:
                print(f"⚠️  无法获取数据数量: {e}")
            
            # 查询贵州茅台相关数据
            try:
                print("\n查询贵州茅台相关数据...")
                results = milvus.collection.query(
                    expr='ts_code == "600519.SH"',
                    output_fields=["ts_code", "ann_date", "title"],
                    limit=5
                )
                
                if results:
                    print(f"✅ 找到 {len(results)} 条贵州茅台数据:")
                    for result in results:
                        print(f"  - {result.get('ann_date', 'N/A')}: {result.get('title', 'N/A')[:50]}...")
                else:
                    print("❌ 未找到贵州茅台数据")
                    
            except Exception as e:
                print(f"❌ 查询贵州茅台数据失败: {e}")
            
            # 查询2024年数据
            try:
                print("\n查询2024年数据...")
                results = milvus.collection.query(
                    expr='ann_date >= "20240101" and ann_date <= "20241231"',
                    output_fields=["ts_code", "ann_date", "title"],
                    limit=5
                )
                
                if results:
                    print(f"✅ 找到 {len(results)} 条2024年数据:")
                    for result in results:
                        print(f"  - {result.get('ts_code', 'N/A')} {result.get('ann_date', 'N/A')}: {result.get('title', 'N/A')[:50]}...")
                else:
                    print("❌ 未找到2024年数据")
                    
            except Exception as e:
                print(f"❌ 查询2024年数据失败: {e}")
                
            # 查询时间范围
            try:
                print("\n查询数据时间范围...")
                # 最早日期
                earliest = milvus.collection.query(
                    expr='ann_date != ""',
                    output_fields=["ann_date"],
                    limit=1000  # 多查一些避免空值
                )
                
                if earliest:
                    dates = [r.get('ann_date', '') for r in earliest if r.get('ann_date')]
                    dates = [d for d in dates if d and len(d) == 8 and d.isdigit()]
                    if dates:
                        dates.sort()
                        print(f"✅ 数据时间范围: {dates[0]} 到 {dates[-1]}")
                        
                        # 检查是否包含2024年
                        has_2024 = any(d.startswith('2024') for d in dates)
                        print(f"{'✅' if has_2024 else '❌'} 包含2024年数据: {has_2024}")
                    else:
                        print("⚠️  无法解析日期格式")
                else:
                    print("❌ 无法获取日期数据")
                    
            except Exception as e:
                print(f"❌ 查询时间范围失败: {e}")
                
        else:
            print("❌ Milvus集合未连接")
            
    except Exception as e:
        print(f"❌ Milvus连接失败: {e}")

def test_without_date_filtering():
    """测试不使用日期过滤的RAG查询"""
    print("\n🔍 测试不使用日期过滤的RAG查询")
    print("=" * 60)
    
    try:
        from database.milvus_connector import MilvusConnector
        from models.embedding_model import EmbeddingModel
        
        milvus = MilvusConnector()
        embedding_model = EmbeddingModel()
        
        # 测试查询：只用股票代码过滤，不用日期过滤
        question = "贵州茅台的经营策略"
        print(f"测试查询: {question}")
        
        # 生成查询向量
        query_vector = embedding_model.encode([question])[0].tolist()
        print(f"✅ 向量生成成功: 维度={len(query_vector)}")
        
        # 只用股票代码过滤
        filter_expr = 'ts_code == "600519.SH"'
        print(f"过滤表达式: {filter_expr}")
        
        # 执行搜索
        results = milvus.search(
            query_vectors=[query_vector],
            top_k=5,
            filter_expr=filter_expr
        )
        
        if results and len(results[0]) > 0:
            print(f"✅ 找到 {len(results[0])} 个结果:")
            for i, hit in enumerate(results[0]):
                ts_code = getattr(hit.entity, 'ts_code', '')
                title = getattr(hit.entity, 'title', '')
                ann_date = getattr(hit.entity, 'ann_date', '')
                score = hit.distance
                print(f"  {i+1}. {ts_code} {ann_date}: {title[:50]}... (相似度: {score:.3f})")
        else:
            print("❌ 未找到结果")
            
        # 测试不用任何过滤
        print(f"\n测试无过滤查询...")
        results_no_filter = milvus.search(
            query_vectors=[query_vector],
            top_k=5,
            filter_expr=None
        )
        
        if results_no_filter and len(results_no_filter[0]) > 0:
            print(f"✅ 无过滤找到 {len(results_no_filter[0])} 个结果:")
            for i, hit in enumerate(results_no_filter[0]):
                ts_code = getattr(hit.entity, 'ts_code', '')
                title = getattr(hit.entity, 'title', '')
                ann_date = getattr(hit.entity, 'ann_date', '')
                score = hit.distance
                print(f"  {i+1}. {ts_code} {ann_date}: {title[:50]}... (相似度: {score:.3f})")
        else:
            print("❌ 无过滤也未找到结果")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主诊断函数"""
    print("🔍 RAG查询智能日期解析干预问题诊断")
    print("目标: 确认智能日期解析是否过度干预RAG查询")
    print("=" * 80)
    
    # 1. 测试智能日期解析的干预
    test_date_intelligence_intervention()
    
    # 2. 检查Milvus中的实际数据
    check_milvus_data()
    
    # 3. 测试不使用日期过滤的查询
    test_without_date_filtering()
    
    print("\n📋 诊断总结:")
    print("1. 检查智能日期解析是否对RAG查询添加了不必要的时间过滤")
    print("2. 确认Milvus中是否包含相关时间段的数据")
    print("3. 验证不使用日期过滤时是否能找到结果")
    print("4. 基于诊断结果决定修复方案")

if __name__ == "__main__":
    main()