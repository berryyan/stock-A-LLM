# 环境备份信息

**备份时间**: 2025-06-26 15:30
**系统信息**: WSL2 Ubuntu 22.04 LTS

## Python环境信息
- Python版本: 3.10.12
- 虚拟环境位置: /mnt/e/PycharmProjects/stock_analysis_system/venv/
- 依赖文件: requirements_backup_20250626.txt

## 关键依赖版本
```
langchain==0.1.20
langchain-community==0.0.38
langchain-core==0.1.52
langchain-openai==0.1.7
fastapi==0.111.0
uvicorn==0.30.1
pymysql==1.1.1
pymilvus==2.4.3
sentence-transformers==3.0.0
pdfplumber==0.11.0
pandas==2.2.2
numpy==1.26.4
```

## Windows Anaconda环境
- Anaconda位置: E:\anaconda3\
- Python版本: 待确认
- 主要用途: 开发IDE环境，即将配置Node.js环境

## 环境恢复命令
```bash
# WSL2环境恢复
cd /mnt/e/PycharmProjects/stock_analysis_system
python3 -m venv venv
source venv/bin/activate
pip install -r backups/environment/requirements_backup_20250626.txt

# 检查GPU支持
python -c "import torch; print(torch.cuda.is_available())"
```

## 注意事项
1. venv目录过大（>2GB），不适合完整备份
2. 使用requirements.txt恢复更加高效
3. Windows Anaconda环境需要单独在Windows系统中备份
4. Node.js环境即将在两边同时配置