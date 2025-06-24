#!/usr/bin/env python3
"""
RAG Agent调试测试脚本
专门测试RAG查询功能，找出API失败原因
"""

import logging
import sys
import os
from datetime import datetime
import traceback

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_rag_query():
    """测试RAG Agent查询功能"""
    logger.info("="*60)
    logger.info("开始测试RAG Agent查询功能")
    logger.info("="*60)
    
    try:
        # 加载环境变量
        from dotenv import load_dotenv
        load_dotenv()
        
        # 创建RAG Agent
        logger.info("1. 创建RAG Agent...")
        from agents.rag_agent import RAGAgent
        
        rag_agent = RAGAgent()
        logger.info("RAG Agent创建成功")
        
        # 执行查询
        query = "贵州茅台2024年的经营策略"
        logger.info(f"2. 执行查询: {query}")
        
        result = rag_agent.query(query)
        
        # 分析结果
        logger.info("3. 查询结果分析:")
        logger.info(f"  成功: {result.get('success', False)}")
        
        if result.get('success'):
            logger.info(f"  找到文档数量: {len(result.get('documents', []))}")
            answer = result.get('answer', '')
            logger.info(f"  答案长度: {len(answer)}")
            logger.info(f"  答案预览: {answer[:200]}...")
            
            # 显示相关文档信息
            docs = result.get('documents', [])
            for i, doc in enumerate(docs[:2]):
                logger.info(f"\n  文档{i+1}:")
                entity = doc.get('entity', {})
                logger.info(f"    标题: {entity.get('title', 'N/A')}")
                logger.info(f"    日期: {entity.get('ann_date', 'N/A')}")
                logger.info(f"    相似度: {doc.get('distance', 'N/A')}")
        else:
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"  查询失败: {error_msg}")
            
            # 尝试分析错误原因
            if 'collection' in error_msg.lower():
                logger.error("  可能的问题: Milvus collection问题")
            elif 'embedding' in error_msg.lower():
                logger.error("  可能的问题: 嵌入模型问题")
            elif 'timeout' in error_msg.lower():
                logger.error("  可能的问题: 超时问题")
        
        # 获取统计信息
        stats = rag_agent.get_stats()
        logger.info(f"\n4. Agent统计:")
        logger.info(f"  查询次数: {stats.get('query_count', 0)}")
        logger.info(f"  成功次数: {stats.get('success_count', 0)}")
        
        return result
        
    except Exception as e:
        logger.error(f"测试失败:")
        logger.error(f"  错误类型: {type(e).__name__}")
        logger.error(f"  错误信息: {str(e)}")
        logger.error(f"  追踪信息:")
        for line in traceback.format_exc().split('\n'):
            if line.strip():
                logger.error(f"    {line}")
        return None

def test_milvus_connection():
    """测试Milvus连接"""
    logger.info("\n" + "="*60)
    logger.info("测试Milvus连接")
    logger.info("="*60)
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from pymilvus import connections, Collection
        
        # 连接参数
        host = os.getenv('MILVUS_HOST', '10.0.0.77')
        port = int(os.getenv('MILVUS_PORT', '19530'))
        user = os.getenv('MILVUS_USER', 'root')
        password = os.getenv('MILVUS_PASSWORD', 'Milvus')
        
        logger.info(f"1. 连接参数: {host}:{port}")
        
        # 建立连接
        connections.connect(
            alias="test",
            host=host,
            port=port,
            user=user,
            password=password
        )
        logger.info("连接成功")
        
        # 检查collection
        collection_name = "stock_announcements"
        collection = Collection(collection_name, using="test")  # 指定连接别名
        logger.info(f"2. Collection: {collection_name}")
        logger.info(f"  实体数量: {collection.num_entities}")
        
        # 检查索引
        try:
            indexes = collection.indexes
            logger.info(f"  索引数量: {len(indexes)}")
            for idx in indexes:
                logger.info(f"    索引字段: {getattr(idx, 'field_name', 'unknown')}")
        except Exception as e:
            logger.info(f"  索引信息获取失败: {e}")
        
        # 加载collection
        collection.load()
        logger.info("Collection加载成功")
        
        # 断开连接
        connections.disconnect("test")
        logger.info("连接已断开")
        
        return True
        
    except Exception as e:
        logger.error(f"Milvus连接失败: {e}")
        return False

def compare_api_vs_direct():
    """对比API调用和直接调用的差异"""
    logger.info("\n" + "="*60)
    logger.info("对比API调用和直接调用")
    logger.info("="*60)
    
    # 读取API日志，查找失败信息
    try:
        api_log_path = "logs/api.log"
        if os.path.exists(api_log_path):
            logger.info("检查API日志...")
            with open(api_log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # 查找最近的RAG相关错误
            rag_errors = []
            for line in lines[-100:]:  # 检查最后100行
                if 'rag' in line.lower() and ('error' in line.lower() or 'failed' in line.lower()):
                    rag_errors.append(line.strip())
            
            if rag_errors:
                logger.info("发现API中的RAG错误:")
                for error in rag_errors[-3:]:  # 显示最后3个错误
                    logger.info(f"  {error}")
            else:
                logger.info("API日志中未发现RAG错误")
        else:
            logger.info("API日志文件不存在")
            
    except Exception as e:
        logger.error(f"读取API日志失败: {e}")
    
    # 检查RAG Agent日志
    try:
        rag_log_path = "logs/rag_agent.log"
        if os.path.exists(rag_log_path):
            logger.info("\n检查RAG Agent日志...")
            with open(rag_log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # 查找最近的日志
            logger.info("最近的RAG Agent日志:")
            recent_logs = lines[-10:]  # 最后10行
            for line in recent_logs:
                if line.strip():
                    logger.info(f"  {line.strip()}")
        else:
            logger.info("RAG Agent日志文件不存在")
            
    except Exception as e:
        logger.error(f"读取RAG日志失败: {e}")

if __name__ == "__main__":
    # 按顺序执行测试
    logger.info("开始RAG Agent调试测试")
    
    # 1. 测试Milvus连接
    milvus_ok = test_milvus_connection()
    
    if milvus_ok:
        # 2. 测试RAG查询
        result = test_rag_query()
        
        # 3. 对比分析
        compare_api_vs_direct()
        
        # 4. 总结
        logger.info("\n" + "="*60)
        if result and result.get('success'):
            logger.info("✅ 直接调用RAG Agent成功！")
            logger.info("这表明RAG Agent本身工作正常，问题可能在API层面")
        else:
            logger.info("❌ 直接调用RAG Agent也失败")
            logger.info("问题在RAG Agent内部或其依赖组件")
    else:
        logger.info("❌ Milvus连接失败，无法继续测试RAG功能")
    
    logger.info("测试完成")
    logger.info("="*60)