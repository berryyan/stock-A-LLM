# 文件名: verify_api.py
# 验证API设置是否正确

import os
import sys

def check_api_files():
    """检查API文件"""
    print("检查API文件...")
    
    api_files = {
        "api/__init__.py": "API包初始化文件",
        "api/main.py": "API主文件（标准名称）",
        "api/api_main.py": "API主文件（当前名称）"
    }
    
    found_files = []
    for file_path, description in api_files.items():
        if os.path.exists(file_path):
            found_files.append(file_path)
            print(f"✓ 找到: {file_path} - {description}")
        else:
            print(f"✗ 缺失: {file_path} - {description}")
    
    return found_files

def test_import():
    """测试导入"""
    print("\n测试导入...")
    
    # 添加项目根目录到路径
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # 测试不同的导入方式
    imports_to_test = [
        ("from api.api_main import app", "api_main.py"),
        ("from api.main import app", "main.py"),
        ("import api.api_main", "api_main 模块"),
        ("import api.main", "main 模块")
    ]
    
    successful_imports = []
    for import_statement, description in imports_to_test:
        try:
            exec(import_statement)
            print(f"✓ 成功导入: {description}")
            successful_imports.append(import_statement)
        except Exception as e:
            print(f"✗ 导入失败 {description}: {e}")
    
    return successful_imports

def suggest_solution(found_files, successful_imports):
    """建议解决方案"""
    print("\n" + "="*60)
    print("建议的解决方案:")
    print("="*60)
    
    if "api/api_main.py" in found_files and "api/main.py" not in found_files:
        print("\n选项1: 重命名文件（推荐）")
        print("在命令行运行:")
        print("cd api")
        print("rename api_main.py main.py")
        
        print("\n选项2: 使用当前文件名")
        print("创建 run_api.py 并使用:")
        print("from api.api_main import app")
        
    elif "api/main.py" in found_files:
        print("\nAPI文件名正确，可以直接运行:")
        print("python -m api.main")
        
    if successful_imports:
        print(f"\n可用的导入语句:")
        for imp in successful_imports:
            print(f"  {imp}")

def main():
    print("API设置验证")
    print("="*60)
    
    # 检查文件
    found_files = check_api_files()
    
    # 测试导入
    successful_imports = test_import()
    
    # 提供建议
    suggest_solution(found_files, successful_imports)
    
    print("\n下一步:")
    print("1. 运行 fix_imports.py 修复代码问题")
    print("2. 根据上面的建议处理API文件")
    print("3. 运行 run_api.py 启动服务")

if __name__ == "__main__":
    main()
