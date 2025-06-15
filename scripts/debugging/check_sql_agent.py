# check_sql_agent.py
# 检查sql_agent.py的语法错误

import ast
import traceback

def check_syntax():
    """检查sql_agent.py的语法"""
    
    file_path = "agents/sql_agent.py"
    
    print("=== 检查SQL Agent语法 ===\n")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试解析为AST
        ast.parse(content)
        print("✅ 语法检查通过")
        
        # 检查特定行
        lines = content.split('\n')
        for i, line in enumerate(lines[235:245], start=236):
            print(f"{i}: {line}")
            
    except SyntaxError as e:
        print(f"❌ 语法错误:")
        print(f"   文件: {e.filename}")
        print(f"   行号: {e.lineno}")
        print(f"   错误: {e.msg}")
        print(f"   问题代码: {e.text}")
        
        # 显示错误位置附近的代码
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print("\n错误位置附近的代码:")
        start = max(0, e.lineno - 5)
        end = min(len(lines), e.lineno + 5)
        
        for i in range(start, end):
            marker = " >>> " if i == e.lineno - 1 else "     "
            print(f"{i+1:4d}{marker}{lines[i].rstrip()}")
            
    except Exception as e:
        print(f"❌ 其他错误: {str(e)}")
        traceback.print_exc()

def find_return_statements():
    """查找所有return语句"""
    
    print("\n=== 查找return语句 ===\n")
    
    file_path = "agents/sql_agent.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        if "return" in line and ("explanation" in line or "final_answer" in line):
            print(f"行 {i+1}: {line.strip()}")

if __name__ == "__main__":
    check_syntax()
    find_return_statements()
