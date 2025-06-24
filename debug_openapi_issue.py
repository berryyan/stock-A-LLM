#!/usr/bin/env python3
"""
调试OpenAPI生成问题的脚本
"""
import sys
import os
import traceback

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 开始调试OpenAPI生成问题...")
    
    # 1. 尝试导入FastAPI应用
    print("1️⃣ 尝试导入FastAPI应用...")
    from api.main import app
    print("✅ FastAPI应用导入成功")
    
    # 2. 尝试生成OpenAPI schema
    print("2️⃣ 尝试生成OpenAPI schema...")
    try:
        openapi_schema = app.openapi()
        print("✅ OpenAPI schema生成成功")
        print(f"📊 Schema包含 {len(openapi_schema.get('paths', {}))} 个端点")
        
        # 检查paths
        paths = openapi_schema.get('paths', {})
        for path, methods in paths.items():
            print(f"  📍 {path}: {list(methods.keys())}")
            
    except Exception as e:
        print(f"❌ OpenAPI schema生成失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        traceback.print_exc()
        
        # 尝试更详细的错误诊断
        print("\n🔧 尝试逐步诊断...")
        
        # 检查Pydantic模型
        try:
            from api.main import QueryRequest, QueryResponse
            print("✅ 基础Pydantic模型导入正常")
            
            # 尝试创建模型实例
            test_request = QueryRequest(question="测试")
            print("✅ QueryRequest模型实例化正常")
            
            test_response = QueryResponse(success=True, question="测试")
            print("✅ QueryResponse模型实例化正常")
            
        except Exception as model_error:
            print(f"❌ Pydantic模型有问题: {model_error}")
            traceback.print_exc()

except ImportError as ie:
    print(f"❌ 导入失败: {ie}")
    traceback.print_exc()
except Exception as e:
    print(f"❌ 未知错误: {e}")
    traceback.print_exc()