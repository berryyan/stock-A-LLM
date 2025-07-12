#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Agent 全面测试套件
基于test-guide-comprehensive.md的完整功能测试
覆盖所有RAG功能，每个功能至少5个正向测试，3个负向测试
"""
import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.rag_agent_modular import RAGAgentModular


class RAGAgentTestRunner:
    """RAG Agent专项测试运行器"""
    
    def __init__(self):
        self.results = {
            "agent": "RAGAgentModular",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "functions": {},
            "details": []
        }
        self.start_time = datetime.now()
        
    def test_case(self, name: str, function: str, category: str = "positive"):
        """测试用例装饰器"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                self.results["total"] += 1
                
                # 初始化功能统计
                if function not in self.results["functions"]:
                    self.results["functions"][function] = {
                        "total": 0,
                        "passed": 0,
                        "failed": 0,
                        "positive_passed": 0,
                        "positive_failed": 0,
                        "negative_passed": 0,
                        "negative_failed": 0
                    }
                
                self.results["functions"][function]["total"] += 1
                
                print(f"\n{'='*80}")
                print(f"测试用例: {name}")
                print(f"功能: {function} | 类型: {'正向测试' if category == 'positive' else '负向测试'}")
                print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print('-'*80)
                
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    elapsed = time.time() - start_time
                    
                    # 判断测试是否通过
                    if category == "positive":
                        test_passed = result.get("success", False)
                    else:
                        test_passed = not result.get("success", True) and "error" in result
                    
                    if test_passed:
                        self.results["passed"] += 1
                        self.results["functions"][function]["passed"] += 1
                        if category == "positive":
                            self.results["functions"][function]["positive_passed"] += 1
                        else:
                            self.results["functions"][function]["negative_passed"] += 1
                        status = "✅ 通过"
                    else:
                        self.results["failed"] += 1
                        self.results["functions"][function]["failed"] += 1
                        if category == "positive":
                            self.results["functions"][function]["positive_failed"] += 1
                        else:
                            self.results["functions"][function]["negative_failed"] += 1
                        status = "❌ 失败"
                    
                    detail = {
                        "name": name,
                        "function": function,
                        "category": category,
                        "status": status,
                        "elapsed": f"{elapsed:.2f}s",
                        "result": result
                    }
                    self.results["details"].append(detail)
                    
                    print(f"状态: {status}")
                    print(f"耗时: {elapsed:.2f}秒")
                    if not test_passed:
                        print(f"详情: {result.get('error', '未知错误')}")
                    
                except Exception as e:
                    elapsed = time.time() - start_time
                    self.results["failed"] += 1
                    self.results["functions"][function]["failed"] += 1
                    if category == "positive":
                        self.results["functions"][function]["positive_failed"] += 1
                    else:
                        self.results["functions"][function]["negative_failed"] += 1
                    
                    detail = {
                        "name": name,
                        "function": function,
                        "category": category,
                        "status": "❌ 异常",
                        "elapsed": f"{elapsed:.2f}s",
                        "error": str(e)
                    }
                    self.results["details"].append(detail)
                    
                    print(f"状态: ❌ 异常")
                    print(f"错误: {str(e)}")
                    
            return wrapper
        return decorator
    
    def print_summary(self):
        """打印测试摘要"""
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        print(f"\n{'='*80}")
        print("RAG Agent 测试摘要")
        print('='*80)
        print(f"总测试数: {self.results['total']}")
        print(f"通过: {self.results['passed']} ({self.results['passed']/self.results['total']*100:.1f}%)")
        print(f"失败: {self.results['failed']} ({self.results['failed']/self.results['total']*100:.1f}%)")
        print(f"总耗时: {total_time:.2f}秒")
        
        print("\n按功能分类的测试结果:")
        print("-"*80)
        print(f"{'功能':<30} {'总计':<8} {'通过':<8} {'失败':<8} {'正向通过':<10} {'负向通过':<10}")
        print("-"*80)
        
        for func_name, stats in self.results["functions"].items():
            print(f"{func_name:<30} {stats['total']:<8} {stats['passed']:<8} {stats['failed']:<8} "
                  f"{stats['positive_passed']:<10} {stats['negative_passed']:<10}")
        
        # 保存详细结果
        with open("rag_agent_comprehensive_results.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细测试结果已保存至: rag_agent_comprehensive_results.json")


# 创建测试运行器
runner = RAGAgentTestRunner()


# ========== 1. 基础公告查询功能测试 ==========

# 正向测试
@runner.test_case("年报查询 - 最新", "基础公告查询", "positive")
def test_annual_report_latest():
    agent = RAGAgentModular()
    return agent.query("贵州茅台的主要业务是什么")

@runner.test_case("季报查询 - 指定季度", "基础公告查询", "positive")
def test_quarterly_report():
    agent = RAGAgentModular()
    return agent.query("宁德时代的发展战略")

@runner.test_case("半年报查询", "基础公告查询", "positive")
def test_semi_annual_report():
    agent = RAGAgentModular()
    return agent.query("中国平安的半年报")

@runner.test_case("重大事项公告", "基础公告查询", "positive")
def test_major_event_announcement():
    agent = RAGAgentModular()
    return agent.query("分析万科A的重大事项公告")

@runner.test_case("公告查询 - 股票代码", "基础公告查询", "positive")
def test_announcement_by_code():
    agent = RAGAgentModular()
    return agent.query("600519.SH的半年报")

@runner.test_case("业绩预告查询", "基础公告查询", "positive")
def test_earnings_forecast():
    agent = RAGAgentModular()
    return agent.query("比亚迪业绩预告")

@runner.test_case("业绩快报查询", "基础公告查询", "positive")
def test_earnings_express():
    agent = RAGAgentModular()
    return agent.query("宁德时代业绩快报")

# 负向测试
@runner.test_case("公告查询 - 空查询", "基础公告查询", "negative")
def test_announcement_empty():
    agent = RAGAgentModular()
    return agent.query("")

@runner.test_case("公告查询 - 不存在股票", "基础公告查询", "negative")
def test_announcement_invalid_stock():
    agent = RAGAgentModular()
    return agent.query("不存在公司的年报")

@runner.test_case("公告查询 - 股票简称", "基础公告查询", "negative")
def test_announcement_abbreviation():
    agent = RAGAgentModular()
    return agent.query("茅台的年报")


# ========== 2. 时间范围查询功能测试 ==========

# 正向测试
@runner.test_case("时间范围 - 指定年份", "时间范围查询", "positive")
def test_time_range_year():
    agent = RAGAgentModular()
    return agent.query("茅台2024年年报")

@runner.test_case("时间范围 - 最近N天", "时间范围查询", "positive")
def test_time_range_recent_days():
    agent = RAGAgentModular()
    return agent.query("茅台最近30天的公告")

@runner.test_case("时间范围 - 今年", "时间范围查询", "positive")
def test_time_range_this_year():
    agent = RAGAgentModular()
    return agent.query("茅台今年的所有公告")

@runner.test_case("时间范围 - 上个月", "时间范围查询", "positive")
def test_time_range_last_month():
    agent = RAGAgentModular()
    return agent.query("平安银行上个月的公告")

@runner.test_case("时间范围 - 日期区间", "时间范围查询", "positive")
def test_time_range_date_interval():
    agent = RAGAgentModular()
    return agent.query("万科A的经营状况分析")

@runner.test_case("时间范围 - 季度", "时间范围查询", "positive")
def test_time_range_quarter():
    agent = RAGAgentModular()
    return agent.query("比亚迪第一季度的公告")

# 负向测试
@runner.test_case("时间范围 - 未来时间", "时间范围查询", "negative")
def test_time_range_future():
    agent = RAGAgentModular()
    return agent.query("贵州茅台2099年的公告")

@runner.test_case("时间范围 - 无效格式", "时间范围查询", "negative")
def test_time_range_invalid_format():
    agent = RAGAgentModular()
    return agent.query("茅台昨天下午3点的公告")

@runner.test_case("时间范围 - 时间冲突", "时间范围查询", "negative")
def test_time_range_conflict():
    agent = RAGAgentModular()
    return agent.query("万科A从2024年6月到2024年1月的公告")


# ========== 3. 公告类型筛选功能测试 ==========

# 正向测试
@runner.test_case("公告类型 - 年度报告", "公告类型筛选", "positive")
def test_announcement_type_annual():
    agent = RAGAgentModular()
    return agent.query("贵州茅台的年度报告")

@runner.test_case("公告类型 - 一季报", "公告类型筛选", "positive")
def test_announcement_type_q1():
    agent = RAGAgentModular()
    return agent.query("万科A一季报")

@runner.test_case("公告类型 - 股东大会决议", "公告类型筛选", "positive")
def test_announcement_type_shareholder():
    agent = RAGAgentModular()
    return agent.query("中国平安股东大会决议")

@runner.test_case("公告类型 - 分红派息", "公告类型筛选", "positive")
def test_announcement_type_dividend():
    agent = RAGAgentModular()
    return agent.query("贵州茅台分红派息公告")

@runner.test_case("公告类型 - 重组公告", "公告类型筛选", "positive")
def test_announcement_type_restructuring():
    agent = RAGAgentModular()
    return agent.query("查询最近的重组公告")

# 负向测试
@runner.test_case("公告类型 - 不存在类型", "公告类型筛选", "negative")
def test_announcement_type_invalid():
    agent = RAGAgentModular()
    return agent.query("贵州茅台的天气预报公告")

@runner.test_case("公告类型 - 混淆类型", "公告类型筛选", "negative")
def test_announcement_type_confused():
    agent = RAGAgentModular()
    return agent.query("万科A的股价公告")

@runner.test_case("公告类型 - 错误组合", "公告类型筛选", "negative")
def test_announcement_type_wrong_combo():
    agent = RAGAgentModular()
    return agent.query("比亚迪的年报季报")


# ========== 4. 主题分析功能测试 ==========

# 正向测试
@runner.test_case("主题分析 - 高端化战略", "主题分析", "positive")
def test_theme_analysis_strategy():
    agent = RAGAgentModular()
    return agent.query("分析茅台的高端化战略")

@runner.test_case("主题分析 - 发展前景", "主题分析", "positive")
def test_theme_analysis_prospect():
    agent = RAGAgentModular()
    return agent.query("比亚迪新能源车发展前景")

@runner.test_case("主题分析 - 行业趋势", "主题分析", "positive")
def test_theme_analysis_trend():
    agent = RAGAgentModular()
    return agent.query("银行业数字化转型趋势")

@runner.test_case("主题分析 - 技术优势", "主题分析", "positive")
def test_theme_analysis_tech():
    agent = RAGAgentModular()
    return agent.query("宁德时代的技术优势")

@runner.test_case("主题分析 - 竞争分析", "主题分析", "positive")
def test_theme_analysis_competition():
    agent = RAGAgentModular()
    return agent.query("分析贵州茅台的竞争优势")

@runner.test_case("主题分析 - 风险因素", "主题分析", "positive")
def test_theme_analysis_risk():
    agent = RAGAgentModular()
    return agent.query("万科A的经营风险分析")

@runner.test_case("主题分析 - 发展战略", "主题分析", "positive")
def test_theme_analysis_development():
    agent = RAGAgentModular()
    return agent.query("中国平安的发展战略")

# 负向测试
@runner.test_case("主题分析 - 无关主题", "主题分析", "negative")
def test_theme_analysis_irrelevant():
    agent = RAGAgentModular()
    return agent.query("分析茅台的足球战略")

@runner.test_case("主题分析 - 空泛查询", "主题分析", "negative")
def test_theme_analysis_vague():
    agent = RAGAgentModular()
    return agent.query("分析一下")

@runner.test_case("主题分析 - 数值查询", "主题分析", "negative")
def test_theme_analysis_numeric():
    agent = RAGAgentModular()
    return agent.query("贵州茅台的股价是多少")


# ========== 5. 关键词搜索功能测试 ==========

# 正向测试
@runner.test_case("关键词搜索 - 精确关键词", "关键词搜索", "positive")
def test_keyword_search_exact():
    agent = RAGAgentModular()
    return agent.query("茅台 白酒")

@runner.test_case("关键词搜索 - 行业关键词", "关键词搜索", "positive")
def test_keyword_search_industry():
    agent = RAGAgentModular()
    return agent.query("宁德时代 电池")

@runner.test_case("关键词搜索 - 多关键词", "关键词搜索", "positive")
def test_keyword_search_multiple():
    agent = RAGAgentModular()
    return agent.query("万科 房地产 销售")

@runner.test_case("关键词搜索 - 模糊关键词", "关键词搜索", "positive")
def test_keyword_search_fuzzy():
    agent = RAGAgentModular()
    return agent.query("新能源 发展")

@runner.test_case("关键词搜索 - 主题关键词", "关键词搜索", "positive")
def test_keyword_search_theme():
    agent = RAGAgentModular()
    return agent.query("数字化 转型")

@runner.test_case("关键词搜索 - 技术关键词", "关键词搜索", "positive")
def test_keyword_search_tech():
    agent = RAGAgentModular()
    return agent.query("人工智能 应用")

@runner.test_case("关键词搜索 - 财务关键词", "关键词搜索", "positive")
def test_keyword_search_finance():
    agent = RAGAgentModular()
    return agent.query("营收 增长")

# 负向测试
@runner.test_case("关键词搜索 - 无效字符", "关键词搜索", "negative")
def test_keyword_search_invalid_chars():
    agent = RAGAgentModular()
    return agent.query("@#$%^&*")

@runner.test_case("关键词搜索 - 超长关键词", "关键词搜索", "negative")
def test_keyword_search_too_long():
    agent = RAGAgentModular()
    return agent.query("这是一个非常非常非常非常非常长的关键词查询测试用例" * 10)

@runner.test_case("关键词搜索 - 矛盾关键词", "关键词搜索", "negative")
def test_keyword_search_contradictory():
    agent = RAGAgentModular()
    return agent.query("上涨 下跌")


# ========== 6. 研报分析功能测试 ==========

# 正向测试
@runner.test_case("研报分析 - 公司战略", "研报分析", "positive")
def test_research_company_strategy():
    agent = RAGAgentModular()
    return agent.query("贵州茅台的公司战略是什么")

@runner.test_case("研报分析 - 业务模式", "研报分析", "positive")
def test_research_business_model():
    agent = RAGAgentModular()
    return agent.query("分析宁德时代的业务模式")

@runner.test_case("研报分析 - 主营业务", "研报分析", "positive")
def test_research_main_business():
    agent = RAGAgentModular()
    return agent.query("万科A的主要业务有哪些")

@runner.test_case("研报分析 - 行业地位", "研报分析", "positive")
def test_research_industry_position():
    agent = RAGAgentModular()
    return agent.query("比亚迪在新能源汽车行业的地位")

@runner.test_case("研报分析 - 管理层分析", "研报分析", "positive")
def test_research_management():
    agent = RAGAgentModular()
    return agent.query("分析贵州茅台的管理层")

@runner.test_case("研报分析 - 产品分析", "研报分析", "positive")
def test_research_product():
    agent = RAGAgentModular()
    return agent.query("宁德时代的主要产品线")

# 负向测试
@runner.test_case("研报分析 - SQL查询误判", "研报分析", "negative")
def test_research_sql_query():
    agent = RAGAgentModular()
    return agent.query("贵州茅台昨天的收盘价")

@runner.test_case("研报分析 - 未来预测", "研报分析", "negative")
def test_research_future_prediction():
    agent = RAGAgentModular()
    return agent.query("预测茅台明年的股价")

@runner.test_case("研报分析 - 个人观点", "研报分析", "negative")
def test_research_personal_opinion():
    agent = RAGAgentModular()
    return agent.query("你觉得应该买入贵州茅台吗")


# ========== 7. 文档相似度搜索功能测试 ==========

# 正向测试
@runner.test_case("相似度搜索 - 高相关性", "文档相似度搜索", "positive")
def test_similarity_high_relevance():
    agent = RAGAgentModular()
    return agent.query("贵州茅台的品牌价值和文化")

@runner.test_case("相似度搜索 - 中等相关性", "文档相似度搜索", "positive")
def test_similarity_medium_relevance():
    agent = RAGAgentModular()
    return agent.query("白酒行业的发展趋势")

@runner.test_case("相似度搜索 - 跨领域搜索", "文档相似度搜索", "positive")
def test_similarity_cross_domain():
    agent = RAGAgentModular()
    return agent.query("ESG和可持续发展")

@runner.test_case("相似度搜索 - 专业术语", "文档相似度搜索", "positive")
def test_similarity_technical_terms():
    agent = RAGAgentModular()
    return agent.query("EBITDA和自由现金流")

@runner.test_case("相似度搜索 - 同义词", "文档相似度搜索", "positive")
def test_similarity_synonyms():
    agent = RAGAgentModular()
    return agent.query("营业收入和销售额")

# 负向测试
@runner.test_case("相似度搜索 - 无关内容", "文档相似度搜索", "negative")
def test_similarity_unrelated():
    agent = RAGAgentModular()
    return agent.query("今天天气怎么样")

@runner.test_case("相似度搜索 - 纯数字", "文档相似度搜索", "negative")
def test_similarity_pure_numbers():
    agent = RAGAgentModular()
    return agent.query("123456789")

@runner.test_case("相似度搜索 - 特殊字符", "文档相似度搜索", "negative")
def test_similarity_special_chars():
    agent = RAGAgentModular()
    return agent.query("!@#$%^&*()")


# ========== 8. 文档源数据展示功能测试 ==========

# 正向测试
@runner.test_case("源数据展示 - 年报来源", "文档源数据展示", "positive")
def test_source_display_annual():
    agent = RAGAgentModular()
    return agent.query("贵州茅台的营收情况如何")

@runner.test_case("源数据展示 - 多文档来源", "文档源数据展示", "positive")
def test_source_display_multiple():
    agent = RAGAgentModular()
    return agent.query("比较茅台和五粮液的品牌战略")

@runner.test_case("源数据展示 - 引用标注", "文档源数据展示", "positive")
def test_source_display_citation():
    agent = RAGAgentModular()
    return agent.query("宁德时代的研发投入情况")

@runner.test_case("源数据展示 - 时间标注", "文档源数据展示", "positive")
def test_source_display_time():
    agent = RAGAgentModular()
    return agent.query("万科A最近的销售数据")

@runner.test_case("源数据展示 - 页码标注", "文档源数据展示", "positive")
def test_source_display_page():
    agent = RAGAgentModular()
    return agent.query("中国平安的风险管理措施")

# 负向测试
@runner.test_case("源数据展示 - 无文档支持", "文档源数据展示", "negative")
def test_source_display_no_docs():
    agent = RAGAgentModular()
    return agent.query("明天的天气预报")

@runner.test_case("源数据展示 - 通用查询", "文档源数据展示", "negative")
def test_source_display_general():
    agent = RAGAgentModular()
    return agent.query("什么是股票")

@runner.test_case("源数据展示 - 计算查询", "文档源数据展示", "negative")
def test_source_display_calculation():
    agent = RAGAgentModular()
    return agent.query("1+1等于多少")


def main():
    """运行所有RAG Agent测试"""
    print("RAG Agent 综合测试套件")
    print("="*80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试配置: 8个功能模块，每个至少5个正向测试和3个负向测试")
    print(f"预期测试用例数: 64+")
    
    # 1. 基础公告查询测试 (10个测试)
    print("\n\n【1. 基础公告查询功能测试】")
    test_annual_report_latest()
    test_quarterly_report()
    test_semi_annual_report()
    test_major_event_announcement()
    test_announcement_by_code()
    test_earnings_forecast()
    test_earnings_express()
    test_announcement_empty()
    test_announcement_invalid_stock()
    test_announcement_abbreviation()
    
    # 2. 时间范围查询测试 (9个测试)
    print("\n\n【2. 时间范围查询功能测试】")
    test_time_range_year()
    test_time_range_recent_days()
    test_time_range_this_year()
    test_time_range_last_month()
    test_time_range_date_interval()
    test_time_range_quarter()
    test_time_range_future()
    test_time_range_invalid_format()
    test_time_range_conflict()
    
    # 3. 公告类型筛选测试 (8个测试)
    print("\n\n【3. 公告类型筛选功能测试】")
    test_announcement_type_annual()
    test_announcement_type_q1()
    test_announcement_type_shareholder()
    test_announcement_type_dividend()
    test_announcement_type_restructuring()
    test_announcement_type_invalid()
    test_announcement_type_confused()
    test_announcement_type_wrong_combo()
    
    # 4. 主题分析测试 (10个测试)
    print("\n\n【4. 主题分析功能测试】")
    test_theme_analysis_strategy()
    test_theme_analysis_prospect()
    test_theme_analysis_trend()
    test_theme_analysis_tech()
    test_theme_analysis_competition()
    test_theme_analysis_risk()
    test_theme_analysis_development()
    test_theme_analysis_irrelevant()
    test_theme_analysis_vague()
    test_theme_analysis_numeric()
    
    # 5. 关键词搜索测试 (10个测试)
    print("\n\n【5. 关键词搜索功能测试】")
    test_keyword_search_exact()
    test_keyword_search_industry()
    test_keyword_search_multiple()
    test_keyword_search_fuzzy()
    test_keyword_search_theme()
    test_keyword_search_tech()
    test_keyword_search_finance()
    test_keyword_search_invalid_chars()
    test_keyword_search_too_long()
    test_keyword_search_contradictory()
    
    # 6. 研报分析测试 (9个测试)
    print("\n\n【6. 研报分析功能测试】")
    test_research_company_strategy()
    test_research_business_model()
    test_research_main_business()
    test_research_industry_position()
    test_research_management()
    test_research_product()
    test_research_sql_query()
    test_research_future_prediction()
    test_research_personal_opinion()
    
    # 7. 文档相似度搜索测试 (8个测试)
    print("\n\n【7. 文档相似度搜索功能测试】")
    test_similarity_high_relevance()
    test_similarity_medium_relevance()
    test_similarity_cross_domain()
    test_similarity_technical_terms()
    test_similarity_synonyms()
    test_similarity_unrelated()
    test_similarity_pure_numbers()
    test_similarity_special_chars()
    
    # 8. 文档源数据展示测试 (8个测试)
    print("\n\n【8. 文档源数据展示功能测试】")
    test_source_display_annual()
    test_source_display_multiple()
    test_source_display_citation()
    test_source_display_time()
    test_source_display_page()
    test_source_display_no_docs()
    test_source_display_general()
    test_source_display_calculation()
    
    # 打印测试摘要
    runner.print_summary()
    
    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"实际测试用例数: {runner.results['total']}")


if __name__ == "__main__":
    main()