#!/usr/bin/env python
"""
测试API文档完整性
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_api_routes():
    """检查API路由配置"""
    print("🔍 检查API路由配置...")
    
    try:
        from api.main import app
        
        routes = []
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                routes.append({
                    'path': route.path,
                    'methods': list(route.methods),
                    'name': getattr(route, 'name', 'unknown'),
                    'tags': getattr(route, 'tags', [])
                })
        
        print(f"📊 总共发现 {len(routes)} 个路由")
        print("\n🛣️ API路由列表:")
        print("=" * 80)
        
        # 按照tags分组显示
        tags_groups = {}
        for route in routes:
            if route['path'].startswith('/'):
                route_tags = route.get('tags', ['未分类'])
                if not route_tags:
                    route_tags = ['未分类']
                
                for tag in route_tags:
                    if tag not in tags_groups:
                        tags_groups[tag] = []
                    tags_groups[tag].append(route)
        
        for tag, tag_routes in sorted(tags_groups.items()):
            print(f"\n📁 {tag}:")
            for route in sorted(tag_routes, key=lambda x: x['path']):
                methods_str = ', '.join(sorted(route['methods']))
                print(f"  {methods_str:12} {route['path']:30} ({route['name']})")
        
        # 检查关键端点
        key_endpoints = [
            '/docs',
            '/redoc', 
            '/',
            '/query',
            '/financial-analysis',
            '/money-flow-analysis',
            '/ws',
            '/health',
            '/status'
        ]
        
        print(f"\n✅ 关键端点检查:")
        missing_endpoints = []
        for endpoint in key_endpoints:
            found = any(route['path'] == endpoint for route in routes)
            status = "✅" if found else "❌"
            print(f"  {status} {endpoint}")
            if not found:
                missing_endpoints.append(endpoint)
        
        if missing_endpoints:
            print(f"\n⚠️ 缺失的关键端点: {missing_endpoints}")
        else:
            print(f"\n🎉 所有关键端点都已配置!")
        
        return len(missing_endpoints) == 0
        
    except Exception as e:
        print(f"❌ 检查API路由失败: {e}")
        return False

def check_api_models():
    """检查API模型定义"""
    print("\n🔍 检查API模型定义...")
    
    try:
        from api.main import (
            QueryRequest, QueryResponse,
            CompareRequest, 
            FinancialAnalysisRequest, FinancialAnalysisResponse,
            MoneyFlowAnalysisRequest, MoneyFlowAnalysisResponse,
            SystemStatus
        )
        
        models = [
            QueryRequest, QueryResponse,
            CompareRequest,
            FinancialAnalysisRequest, FinancialAnalysisResponse,
            MoneyFlowAnalysisRequest, MoneyFlowAnalysisResponse,
            SystemStatus
        ]
        
        print(f"📋 发现 {len(models)} 个Pydantic模型:")
        for model in models:
            print(f"  ✅ {model.__name__}")
            
        print(f"\n🎉 所有API模型定义完整!")
        return True
        
    except Exception as e:
        print(f"❌ 检查API模型失败: {e}")
        return False

def check_tags_metadata():
    """检查标签元数据"""
    print("\n🔍 检查API标签元数据...")
    
    try:
        from api.main import app
        
        tags_metadata = getattr(app, 'openapi_tags', None)
        if not tags_metadata:
            print("⚠️ 未发现标签元数据配置")
            return False
        
        print(f"🏷️ 发现 {len(tags_metadata)} 个标签分组:")
        for tag in tags_metadata:
            print(f"  📁 {tag['name']}: {tag['description']}")
        
        print(f"\n🎉 标签元数据配置完整!")
        return True
        
    except Exception as e:
        print(f"❌ 检查标签元数据失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始检查API文档完整性")
    print("=" * 80)
    
    # 执行各项检查
    checks = [
        check_api_routes(),
        check_api_models(),
        check_tags_metadata()
    ]
    
    # 汇总结果
    print("\n" + "=" * 80)
    print("📊 检查结果汇总:")
    
    check_names = [
        "API路由配置",
        "API模型定义", 
        "标签元数据配置"
    ]
    
    for i, (check_name, result) in enumerate(zip(check_names, checks)):
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {check_name}: {status}")
    
    all_passed = all(checks)
    if all_passed:
        print(f"\n🎉 所有检查通过! API文档已完整更新。")
        print(f"📖 您可以访问 http://localhost:8000/docs 查看完整的API文档。")
    else:
        print(f"\n⚠️ 部分检查失败，请查看上面的详细信息。")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)