# 文件名: install_dependencies.py
# 在项目根目录下创建并运行

import subprocess
import sys

def install_package(package):
    """安装单个包"""
    print(f"Installing {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    """主函数"""
    print("Installing Agent modules and API dependencies...")
    print("="*60)
    
    packages = [
        # LangChain核心包
        "langchain==0.2.0",
        "langchain-community==0.2.0",
        "langchain-experimental==0.0.64",
        "langgraph==0.2.0",
        
        # LLM支持包
        "langchain-openai==0.1.0",
        "openai==1.30.0",
        
        # FastAPI相关包
        "fastapi==0.109.0",
        "uvicorn[standard]==0.27.0",
        "python-multipart==0.0.6",
        "websockets==12.0",
        
        # 其他依赖
        "pydantic==2.5.3",
        "typing-extensions==4.9.0",
    ]
    
    failed_packages = []
    
    for package in packages:
        try:
            install_package(package)
            print(f"✓ {package} installed successfully\n")
        except Exception as e:
            print(f"✗ Failed to install {package}: {e}\n")
            failed_packages.append(package)
    
    print("="*60)
    if failed_packages:
        print(f"Failed to install: {', '.join(failed_packages)}")
        print("Please try installing them manually.")
    else:
        print("All packages installed successfully!")
        print("\nYou can now start the API server with:")
        print("python -m api.main")

if __name__ == "__main__":
    main()
