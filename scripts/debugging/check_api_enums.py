# check_api_enums.py
import requests
import json

def check_api_schema():
    """检查API的OpenAPI schema"""
    try:
        response = requests.get("http://localhost:8000/openapi.json")
        if response.status_code == 200:
            schema = response.json()
            
            # 查找QueryType的定义
            if "components" in schema and "schemas" in schema["components"]:
                schemas = schema["components"]["schemas"]
                
                # 打印所有枚举类型
                print("=== API中定义的枚举类型 ===\n")
                
                for name, definition in schemas.items():
                    if "enum" in definition:
                        print(f"{name}:")
                        print(f"  枚举值: {definition['enum']}")
                        print(f"  类型: {definition.get('type', 'string')}")
                        print()
                        
                # 特别查找QueryType
                if "QueryType" in schemas:
                    print("=== QueryType 定义 ===")
                    print(json.dumps(schemas["QueryType"], indent=2))
                    
                # 查找QueryRequest
                if "QueryRequest" in schemas:
                    print("\n=== QueryRequest 定义 ===")
                    print(json.dumps(schemas["QueryRequest"], indent=2))
                    
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    check_api_schema()