#!/bin/bash
# 运行系统测试的便捷脚本

echo "股票分析系统测试工具"
echo "===================="
echo "1. 快速功能测试 (2-3分钟)"
echo "2. 综合系统测试 (10-15分钟)"
echo "3. 基线功能测试"
echo "4. 财务分析测试"
echo "5. 启动API服务"
echo "===================="

read -p "请选择测试类型 (1-5): " choice

case $choice in
    1)
        echo "运行快速功能测试..."
        source venv/bin/activate && python quick_system_test.py
        ;;
    2)
        echo "运行综合系统测试..."
        source venv/bin/activate && python comprehensive_system_test.py
        ;;
    3)
        echo "运行基线功能测试..."
        source venv/bin/activate && python baseline_test.py
        ;;
    4)
        echo "运行财务分析测试..."
        source venv/bin/activate && python test_financial_agent.py
        ;;
    5)
        echo "启动API服务..."
        source venv/bin/activate && python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
        ;;
    *)
        echo "无效选择"
        ;;
esac