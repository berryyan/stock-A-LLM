"""
测试各个组件是否正常工作
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.milvus_connector import MilvusConnector
from agents.rag_agent import RAGAgent

def test_milvus():
    """测试 Milvus 连接"""
    print("测试 Milvus 连接...")
    try:
        milvus = MilvusConnector()
        print(f"✅ Milvus 连接成功")
        print(f"   集合名: {milvus.collection_name}")
        print(f"   实体数: {milvus.collection.num_entities}")
        
        # 尝试搜索
        test_vector = [0.1] * 1024  # BGE-M3 是 1024 维
        results = milvus.search(
            vectors=[test_vector],
            limit=1
        )
        print(f"✅ 搜索测试成功")
        return True
    except Exception as e:
        print(f"❌ Milvus 测试失败: {e}")
        return False

def test_rag():
    """测试 RAG Agent"""
    print("\n测试 RAG Agent...")
    try:
        rag = RAGAgent()
        result = rag.query("贵州茅台2024年年报")
        print(f"✅ RAG Agent 测试成功")
        print(f"   返回类型: {type(result)}")
        return True
    except Exception as e:
        print(f"❌ RAG Agent 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("组件测试")
    print("=" * 60)
    
    test_milvus()
    test_rag()
