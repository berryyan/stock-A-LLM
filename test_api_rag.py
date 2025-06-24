#!/usr/bin/env python3
"""
测试API层面的RAG查询问题
对比API调用和直接调用的差异
"""

import logging
import sys
import os
import requests
import json
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

def test_api_query():
    """测试通过API调用RAG查询"""
    logger.info("="*60)
    logger.info("测试API层面的RAG查询")
    logger.info("="*60)
    
    try:
        # API服务器地址
        api_url = "http://localhost:8000/query"
        
        # 测试查询
        query = "贵州茅台2024年的经营策略"
        
        # 构造请求数据
        request_data = {
            "query": query,
            "query_type": "rag"  # 强制使用RAG查询
        }
        
        logger.info(f"1. 发送API请求:")
        logger.info(f"   URL: {api_url}")
        logger.info(f"   查询: {query}")
        logger.info(f"   类型: rag")
        
        # 发送请求
        response = requests.post(
            api_url,
            json=request_data,
            timeout=60
        )
        
        logger.info(f"2. API响应:")
        logger.info(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"   成功: {result.get('success', False)}")
            
            if result.get('success'):
                answer = result.get('answer', '')
                logger.info(f"   答案长度: {len(answer)}")
                logger.info(f"   答案预览: {answer[:200]}...")
            else:
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"   错误: {error_msg}")
                
                # 检查详细错误信息
                if 'details' in result:
                    logger.error(f"   详细错误: {result['details']}")
        else:
            logger.error(f"   HTTP错误: {response.text}")
            
        return response.status_code == 200 and result.get('success', False)
        
    except requests.exceptions.ConnectionError:
        logger.error("无法连接到API服务器")
        logger.error("请确保API服务器正在运行: python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        logger.error(f"API测试失败: {e}")
        logger.error(f"追踪信息: {traceback.format_exc()}")
        return False

def test_hybrid_agent():
    """直接测试Hybrid Agent的RAG路由"""
    logger.info("\n" + "="*60)
    logger.info("测试Hybrid Agent的RAG路由")
    logger.info("="*60)
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # 创建Hybrid Agent
        from agents.hybrid_agent import HybridAgent
        
        hybrid_agent = HybridAgent()
        logger.info("Hybrid Agent创建成功")
        
        # 测试查询
        query = "贵州茅台2024年的经营策略"
        logger.info(f"查询: {query}")
        
        result = hybrid_agent.query(query)
        
        logger.info(f"结果:")
        logger.info(f"  成功: {result.get('success', False)}")
        logger.info(f"  查询类型: {result.get('query_type', 'unknown')}")
        
        if result.get('success'):
            answer = result.get('answer', '')
            logger.info(f"  答案长度: {len(answer)}")
            logger.info(f"  答案预览: {answer[:200]}...")
        else:
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"  错误: {error_msg}")
            
        return result.get('success', False)
        
    except Exception as e:
        logger.error(f"Hybrid Agent测试失败: {e}")
        logger.error(f"追踪信息: {traceback.format_exc()}")
        return False

def compare_api_vs_agents():
    """对比API和Agent的差异"""
    logger.info("\n" + "="*60)
    logger.info("对比API和Agent调用结果")
    logger.info("="*60)
    
    # 测试直接RAG Agent
    logger.info("1. 直接RAG Agent测试:")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from agents.rag_agent import RAGAgent
        rag_agent = RAGAgent()
        
        query = "贵州茅台2024年的经营策略"
        result = rag_agent.query(query)
        
        rag_success = result.get('success', False)
        logger.info(f"   RAG Agent直接调用: {'✅ 成功' if rag_success else '❌ 失败'}")
        
        if not rag_success:
            logger.error(f"   错误: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"   RAG Agent直接调用失败: {e}")
        rag_success = False
    
    # 测试Hybrid Agent
    logger.info("\n2. Hybrid Agent测试:")
    hybrid_success = test_hybrid_agent()
    
    # 测试API
    logger.info("\n3. API测试:")
    api_success = test_api_query()
    
    # 总结
    logger.info("\n" + "="*60)
    logger.info("测试结果总结:")
    logger.info(f"  RAG Agent直接调用: {'✅ 成功' if rag_success else '❌ 失败'}")
    logger.info(f"  Hybrid Agent调用:  {'✅ 成功' if hybrid_success else '❌ 失败'}")
    logger.info(f"  API调用:           {'✅ 成功' if api_success else '❌ 失败'}")
    
    if rag_success and not api_success:
        logger.info("\n🔍 分析: RAG Agent工作正常，但API调用失败")
        logger.info("可能的原因:")
        logger.info("  1. API请求格式问题")
        logger.info("  2. API路由逻辑问题")
        logger.info("  3. API错误处理问题")
        logger.info("  4. 权限或认证问题")
    elif not rag_success:
        logger.info("\n🔍 分析: RAG Agent本身有问题")
    else:
        logger.info("\n🔍 分析: 所有组件都工作正常")

def check_api_server():
    """检查API服务器状态"""
    logger.info("\n" + "="*60)
    logger.info("检查API服务器状态")
    logger.info("="*60)
    
    try:
        # 检查健康端点
        health_url = "http://localhost:8000/health"
        response = requests.get(health_url, timeout=5)
        
        if response.status_code == 200:
            health_data = response.json()
            logger.info("✅ API服务器运行正常")
            logger.info(f"   状态: {health_data.get('status', 'unknown')}")
            
            # 检查组件状态
            components = health_data.get('components', {})
            for component, status in components.items():
                logger.info(f"   {component}: {status}")
                
        else:
            logger.error(f"❌ API服务器健康检查失败: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        logger.error("❌ 无法连接到API服务器")
        logger.error("请启动API服务器: python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        logger.error(f"❌ API服务器检查失败: {e}")

if __name__ == "__main__":
    logger.info("开始API与Agent对比测试")
    
    # 1. 检查API服务器
    check_api_server()
    
    # 2. 执行对比测试
    compare_api_vs_agents()
    
    logger.info("\n测试完成！")