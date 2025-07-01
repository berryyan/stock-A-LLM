#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API端点验证脚本
用于快速检查所有API端点的可用性
"""

import requests
import json
from datetime import datetime
from typing import List, Tuple, Dict

# API基础URL
BASE_URL = "http://localhost:8000"

# 定义要测试的端点
ENDPOINTS = [
    # (路径, 方法, 描述, 测试数据)
    ("/", "GET", "前端首页", None),
    ("/chat", "GET", "聊天界面", None),
    ("/api", "GET", "API信息", None),
    ("/health", "GET", "健康检查", None),
    ("/status", "GET", "系统状态", None),
    ("/docs", "GET", "API文档", None),
    ("/query", "POST", "通用查询接口", {
        "question": "贵州茅台最新股价",
        "query_type": "sql"
    }),
    ("/compare", "POST", "公司对比接口", {
        "companies": ["600519.SH", "000858.SZ"],
        "metrics": ["revenue", "profit"]
    }),
    ("/financial-analysis", "POST", "财务分析接口", {
        "stock": "600519.SH",
        "analysis_type": "health_score"
    }),
    ("/money-flow-analysis", "POST", "资金流向接口", {
        "stock": "300750.SZ",
        "days": 30
    }),
    ("/companies", "GET", "公司列表查询", {"params": {"limit": 5}}),
    ("/reports/recent", "GET", "最近报告查询", {"params": {"ts_code": "600519.SH", "days": 30}}),
    ("/suggestions", "GET", "查询建议", {"params": {"q": "茅台"}}),
    ("/query/stream", "POST", "流式查询", {
        "question": "测试查询",
        "query_type": "sql"
    }),
]

def test_endpoint(path: str, method: str, data: Dict = None) -> Tuple[bool, int, str]:
    """测试单个端点"""
    url = BASE_URL + path
    
    try:
        if method == "GET":
            if data and "params" in data:
                response = requests.get(url, params=data["params"], timeout=5)
            else:
                response = requests.get(url, timeout=5)
        elif method == "POST":
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            return False, 0, f"不支持的方法: {method}"
        
        return True, response.status_code, "成功"
    except requests.exceptions.ConnectionError:
        return False, 0, "连接失败（服务未启动？）"
    except requests.exceptions.Timeout:
        return False, 0, "请求超时"
    except Exception as e:
        return False, 0, f"错误: {str(e)}"

def main():
    """主函数"""
    print("=" * 80)
    print(f"API端点验证 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"基础URL: {BASE_URL}")
    print("=" * 80)
    
    # 首先测试服务是否运行
    print("\n检查服务状态...")
    success, status_code, message = test_endpoint("/health", "GET")
    if not success:
        print(f"❌ 服务未运行: {message}")
        print("\n请先启动API服务:")
        print("python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    print("✅ 服务运行正常\n")
    
    # 测试所有端点
    results = []
    total = len(ENDPOINTS)
    success_count = 0
    
    print("测试端点:")
    print("-" * 80)
    
    for path, method, desc, data in ENDPOINTS:
        success, status_code, message = test_endpoint(path, method, data)
        
        if success and status_code == 200:
            status_icon = "✅"
            success_count += 1
        elif success and status_code == 422:
            status_icon = "⚠️"
            message = "参数验证失败"
        elif success:
            status_icon = "⚠️"
            message = f"状态码: {status_code}"
        else:
            status_icon = "❌"
        
        results.append({
            "path": path,
            "method": method,
            "desc": desc,
            "success": success,
            "status_code": status_code,
            "message": message,
            "icon": status_icon
        })
        
        print(f"{status_icon} {method:6} {path:30} | {desc:20} | {message}")
    
    # 汇总结果
    print("\n" + "=" * 80)
    print(f"测试结果汇总: {success_count}/{total} 成功")
    print("=" * 80)
    
    # 列出失败的端点
    failed = [r for r in results if r["icon"] == "❌"]
    if failed:
        print("\n失败的端点:")
        for r in failed:
            print(f"- {r['method']} {r['path']}: {r['message']}")
    
    # 列出警告的端点
    warnings = [r for r in results if r["icon"] == "⚠️"]
    if warnings:
        print("\n需要注意的端点:")
        for r in warnings:
            print(f"- {r['method']} {r['path']}: {r['message']}")
    
    # 建议
    print("\n建议:")
    if success_count == total:
        print("✅ 所有端点正常工作")
    else:
        print("- 检查失败端点的实现")
        print("- 验证测试参数是否正确")
        print("- 查看API日志获取详细错误信息")

if __name__ == "__main__":
    main()