#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试前端市值排名显示效果
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json

def test_frontend_query():
    """通过API测试市值排名查询"""
    
    # API配置
    api_url = "http://localhost:8000/query"
    headers = {
        "Content-Type": "application/json"
    }
    
    # 测试查询
    test_queries = [
        "总市值排名",
        "市值TOP5",
        "流通市值排名前5",
        "今天的市值排名"
    ]
    
    print("前端市值排名测试")
    print("=" * 80)
    print("注意：请确保API服务器正在运行 (http://localhost:8000)")
    print("")
    
    for query in test_queries:
        print(f"\n查询: {query}")
        print("-" * 60)
        
        try:
            # 发送请求
            response = requests.post(
                api_url,
                headers=headers,
                json={"query": query},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    print("✅ 查询成功")
                    print("\n返回结果预览:")
                    # 只显示前500字符
                    content = result.get("result", "")
                    if len(content) > 500:
                        print(content[:500] + "...")
                    else:
                        print(content)
                    
                    # 检查是否使用了快速路径
                    if result.get("quick_path"):
                        print("\n⚡ 使用了快速路由")
                    
                    # 检查返回格式
                    if "| 排名 |" in content and "## " in content:
                        print("✅ 格式正确：Markdown表格")
                    else:
                        print("⚠️ 格式可能需要检查")
                        
                else:
                    print(f"❌ 查询失败: {result.get('error', '未知错误')}")
                    
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(response.text)
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败：请确保API服务器正在运行")
            print("   运行命令: python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
            break
        except Exception as e:
            print(f"❌ 执行异常: {str(e)}")


def show_markdown_example():
    """显示Markdown表格示例"""
    
    print("\n\nMarkdown表格在前端的渲染效果")
    print("=" * 80)
    
    example = """## 总市值排名 - 2025-07-01

| 排名 | 股票名称 | 股票代码 | 股价(元) | 涨跌幅 | 总市值(亿) |
|------|----------|----------|----------|--------|------------|
| 1 | 工商银行 | 601398.SH | 7.66 | 0.92% | 27300.70 |
| 2 | 建设银行 | 601939.SH | 9.71 | 2.86% | 25401.40 |
| 3 | 中国移动 | 600941.SH | 112.56 | 0.01% | 24320.00 |"""
    
    print("原始Markdown:")
    print(example)
    
    print("\n前端组件说明:")
    print("- 使用 react-markdown 渲染")
    print("- 支持 GFM (GitHub Flavored Markdown)")
    print("- 表格自动美化，响应式布局")
    print("- 深色模式下自动调整颜色")


if __name__ == "__main__":
    # 测试API查询
    test_frontend_query()
    
    # 显示Markdown示例
    show_markdown_example()