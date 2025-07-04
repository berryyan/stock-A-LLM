# 查询系统模块化重构方案

**版本**: v1.0  
**日期**: 2025-07-05  
**作者**: Claude Code Assistant  

## 一、背景与目标

### 1.1 当前问题

1. **代码重复严重**：
   - 每个Agent都有自己的参数提取逻辑
   - 验证逻辑分散在各处
   - 错误处理不一致

2. **维护困难**：
   - 修改一个功能需要改多处代码
   - 新增功能需要在多个Agent中实现
   - 测试覆盖困难

3. **扩展性差**：
   - 新增查询类型需要大量重复代码
   - 难以统一管理查询行为
   - 缺乏清晰的模块边界

### 1.2 重构目标

1. **代码复用最大化**：所有公共功能抽取为独立模块
2. **职责单一化**：每个模块只负责一个功能
3. **接口标准化**：统一的输入输出格式
4. **错误处理统一化**：集中式错误管理
5. **测试友好化**：易于单元测试和集成测试

## 二、模块架构设计

### 2.1 核心模块层次

```
应用层（Application Layer）
├── API层（API Layer）
│   ├── /query 接口
│   ├── /financial-analysis 接口
│   └── /money-flow-analysis 接口
│
├── Agent层（Agent Layer）
│   ├── SQL Agent
│   ├── RAG Agent
│   ├── Financial Agent
│   ├── Money Flow Agent
│   └── Hybrid Agent（路由器）
│
├── 公共服务层（Common Service Layer）
│   ├── 参数处理模块（Parameter Processing）
│   │   ├── parameter_extractor.py
│   │   ├── query_validator.py
│   │   └── parameter_converter.py
│   │
│   ├── 数据处理模块（Data Processing）
│   │   ├── stock_validation_helper.py ✓
│   │   ├── date_intelligence.py ✓
│   │   └── metric_calculator.py
│   │
│   ├── 结果处理模块（Result Processing）
│   │   ├── result_formatter.py
│   │   ├── table_generator.py
│   │   └── response_builder.py
│   │
│   └── 错误处理模块（Error Handling）
│       ├── error_handler.py
│       ├── error_codes.py
│       └── user_messages.py
│
└── 基础设施层（Infrastructure Layer）
    ├── 数据库连接（Database）
    ├── 缓存管理（Cache）
    └── 日志系统（Logging）
```

### 2.2 模块详细设计

#### 2.2.1 参数提取器（parameter_extractor.py）

```python
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class ExtractedParams:
    """提取的参数数据类"""
    stocks: List[str] = None          # 股票列表
    date: str = None                  # 单个日期
    date_range: Tuple[str, str] = None # 日期范围
    limit: int = 10                   # 数量限制
    order_by: str = 'DESC'            # 排序方式
    metrics: List[str] = None         # 指标列表
    period: str = None                # 报告期
    exclude_st: bool = False          # 排除ST
    sector: str = None                # 板块名称
    
class ParameterExtractor:
    """统一的参数提取器"""
    
    def extract_all_params(self, query: str, template: QueryTemplate) -> ExtractedParams:
        """从查询中提取所有参数"""
        params = ExtractedParams()
        
        # 根据模板需求提取相应参数
        if template.requires_stock:
            params.stocks = self._extract_stocks(query)
        
        if template.requires_date:
            params.date = self._extract_date(query)
        
        if template.requires_date_range:
            params.date_range = self._extract_date_range(query)
        
        if template.requires_limit:
            params.limit = self._extract_limit(query, template.default_limit)
        
        if template.supports_exclude_st:
            params.exclude_st = self._check_exclude_st(query)
        
        # 提取其他参数...
        
        return params
    
    def _extract_stocks(self, query: str) -> List[str]:
        """提取股票信息"""
        # 使用unified_stock_validator提取
        from utils.unified_stock_validator import UnifiedStockValidator
        validator = UnifiedStockValidator()
        return validator.extract_multiple_stocks(query)
    
    def _extract_date(self, query: str) -> str:
        """提取单个日期"""
        from utils.date_intelligence import date_intelligence
        # 实现日期提取逻辑
        pass
    
    def _extract_date_range(self, query: str) -> Tuple[str, str]:
        """提取日期范围"""
        # 实现日期范围提取逻辑
        pass
    
    def _extract_limit(self, query: str, default: int) -> int:
        """提取数量限制"""
        from utils.chinese_number_converter import extract_limit_from_query
        return extract_limit_from_query(query) or default
```

#### 2.2.2 查询验证器（query_validator.py）

```python
from typing import Tuple, Dict, Any
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    error_code: str = None
    error_detail: Dict[str, Any] = None
    
class QueryValidator:
    """统一的查询验证器"""
    
    def validate_params(self, params: ExtractedParams, template: QueryTemplate) -> ValidationResult:
        """验证提取的参数"""
        # 验证必需参数
        for field in template.required_fields:
            if not hasattr(params, field) or getattr(params, field) is None:
                return ValidationResult(
                    is_valid=False,
                    error_code="MISSING_REQUIRED_FIELD",
                    error_detail={"field": field}
                )
        
        # 验证股票
        if params.stocks:
            result = self._validate_stocks(params.stocks)
            if not result.is_valid:
                return result
        
        # 验证日期
        if params.date:
            result = self._validate_date(params.date)
            if not result.is_valid:
                return result
        
        # 验证其他参数...
        
        return ValidationResult(is_valid=True)
    
    def _validate_stocks(self, stocks: List[str]) -> ValidationResult:
        """验证股票列表"""
        from utils.stock_validation_helper import validate_stock_list
        results = validate_stock_list(stocks)
        
        for i, (success, ts_code, stock_name, error_msg) in enumerate(results):
            if not success:
                return ValidationResult(
                    is_valid=False,
                    error_code="INVALID_STOCK",
                    error_detail={"stock": stocks[i], "message": error_msg}
                )
        
        return ValidationResult(is_valid=True)
```

#### 2.2.3 结果格式化器（result_formatter.py）

```python
from typing import List, Dict, Any
import pandas as pd

class ResultFormatter:
    """统一的结果格式化器"""
    
    def format_result(self, data: Any, format_type: str, template: QueryTemplate) -> str:
        """根据类型格式化结果"""
        if format_type == "ranking_table":
            return self.format_ranking_table(data, template)
        elif format_type == "financial_table":
            return self.format_financial_table(data, template)
        elif format_type == "kline_data":
            return self.format_kline_data(data, template)
        elif format_type == "money_flow":
            return self.format_money_flow(data, template)
        else:
            return self.format_generic_table(data)
    
    def format_ranking_table(self, data: List[Dict], template: QueryTemplate) -> str:
        """格式化排名表格"""
        if not data:
            return "查询无结果"
        
        # 提取显示列
        columns = template.default_params.get('display_columns', list(data[0].keys()))
        
        # 创建表格
        rows = []
        rows.append("| 排名 | " + " | ".join(columns) + " |")
        rows.append("|------|" + "|------" * len(columns) + "|")
        
        for idx, row in enumerate(data, 1):
            values = [str(row.get(col, '')) for col in columns]
            rows.append(f"| {idx} | " + " | ".join(values) + " |")
        
        return "\n".join(rows)
    
    def format_financial_table(self, data: Dict, template: QueryTemplate) -> str:
        """格式化财务数据表格"""
        # 实现财务数据格式化逻辑
        pass
    
    def format_kline_data(self, data: List[Dict], template: QueryTemplate) -> str:
        """格式化K线数据"""
        if not data:
            return "查询无结果"
        
        # 使用pandas格式化
        df = pd.DataFrame(data)
        
        # 格式化数值列
        numeric_columns = ['open', 'high', 'low', 'close', 'vol', 'amount']
        for col in numeric_columns:
            if col in df.columns:
                if col in ['vol', 'amount']:
                    df[col] = df[col].apply(lambda x: f"{x/10000:.2f}万" if x >= 10000 else str(x))
                else:
                    df[col] = df[col].apply(lambda x: f"{x:.2f}")
        
        return df.to_markdown(index=False)
```

#### 2.2.4 错误处理器（error_handler.py）

```python
from typing import Dict, Any
import traceback

class ErrorHandler:
    """统一的错误处理器"""
    
    # 错误码定义
    ERROR_CODES = {
        # 股票相关错误
        "STOCK_NOT_FOUND": "找不到股票：{stock}",
        "INVALID_STOCK_FORMAT": "股票代码格式错误：{format_error}",
        "INVALID_STOCK_CASE": "证券代码后缀大小写错误，应为{correct_case}",
        "USE_FULL_NAME": "请使用完整公司名称，如：{full_name}",
        
        # 日期相关错误
        "INVALID_DATE": "日期格式错误：{date}",
        "DATE_OUT_OF_RANGE": "日期超出有效范围：{date}",
        "NO_TRADING_DATA": "该日期没有交易数据：{date}",
        
        # 参数相关错误
        "MISSING_REQUIRED_PARAM": "缺少必需参数：{param}",
        "INVALID_LIMIT": "数量限制必须在1-1000之间，当前值：{limit}",
        "INVALID_METRIC": "不支持的指标：{metric}",
        
        # 系统错误
        "DATABASE_ERROR": "数据库查询错误",
        "NETWORK_ERROR": "网络连接错误",
        "TIMEOUT_ERROR": "查询超时",
        "UNKNOWN_ERROR": "未知错误"
    }
    
    def handle_error(self, error_code: str, detail: Dict[str, Any] = None, exception: Exception = None) -> Dict[str, Any]:
        """处理错误并返回标准化响应"""
        error_message = self._get_error_message(error_code, detail)
        
        response = {
            "success": False,
            "error": error_message,
            "error_code": error_code,
            "detail": detail
        }
        
        # 如果有异常，添加调试信息（仅在开发模式）
        if exception and self._is_debug_mode():
            response["debug_info"] = {
                "exception_type": type(exception).__name__,
                "exception_message": str(exception),
                "traceback": traceback.format_exc()
            }
        
        return response
    
    def _get_error_message(self, error_code: str, detail: Dict[str, Any] = None) -> str:
        """获取用户友好的错误消息"""
        template = self.ERROR_CODES.get(error_code, "发生错误：{error_code}")
        
        if detail:
            try:
                return template.format(**detail)
            except:
                return template
        
        return template.format(error_code=error_code)
    
    def _is_debug_mode(self) -> bool:
        """检查是否为调试模式"""
        import os
        return os.getenv("DEBUG", "false").lower() == "true"
```

### 2.3 模块集成示例

展示如何在SQL Agent中使用这些模块：

```python
# 在sql_agent.py中的使用示例

from utils.parameter_extractor import ParameterExtractor
from utils.query_validator import QueryValidator
from utils.result_formatter import ResultFormatter
from utils.error_handler import ErrorHandler

class SQLAgent:
    def __init__(self):
        # 初始化公共模块
        self.param_extractor = ParameterExtractor()
        self.validator = QueryValidator()
        self.formatter = ResultFormatter()
        self.error_handler = ErrorHandler()
    
    def _try_quick_query_v2(self, processed_query: str) -> Optional[Dict]:
        """使用模块化方法的快速查询"""
        # 1. 模板匹配
        template, params = match_query_template(processed_query)
        if not template:
            return None
        
        # 2. 参数提取
        extracted_params = self.param_extractor.extract_all_params(
            processed_query, template
        )
        
        # 3. 参数验证
        validation_result = self.validator.validate_params(
            extracted_params, template
        )
        
        if not validation_result.is_valid:
            # 4. 错误处理
            return self.error_handler.handle_error(
                validation_result.error_code,
                validation_result.error_detail
            )
        
        try:
            # 5. 执行查询
            sql_template = SQLTemplates.TEMPLATES.get(template.name)
            if not sql_template:
                return None
            
            # 构建SQL参数
            sql_params = self._build_sql_params(extracted_params, template)
            
            # 执行SQL
            result = self._execute_sql(sql_template, sql_params)
            
            # 6. 格式化结果
            formatted_result = self.formatter.format_result(
                result,
                template.default_params.get('format_type', 'generic_table'),
                template
            )
            
            return {
                'success': True,
                'result': formatted_result,
                'sql': sql_template.format(**sql_params),
                'quick_path': True
            }
            
        except Exception as e:
            # 7. 异常处理
            return self.error_handler.handle_error(
                "DATABASE_ERROR",
                {"error": str(e)},
                exception=e
            )
```

## 三、实施计划

### 3.1 第一阶段：创建基础模块（2天）

1. **Day 1**：
   - 创建parameter_extractor.py
   - 创建query_validator.py
   - 编写单元测试

2. **Day 2**：
   - 创建result_formatter.py
   - 创建error_handler.py
   - 编写集成测试

### 3.2 第二阶段：模块集成（3天）

1. **Day 3**：
   - 在SQL Agent中集成新模块
   - 逐步替换原有代码
   - 确保功能不受影响

2. **Day 4**：
   - 在其他Agent中集成
   - 统一错误处理流程
   - 优化性能

3. **Day 5**：
   - 完整测试
   - 修复发现的问题
   - 更新文档

### 3.3 第三阶段：扩展优化（2天）

1. **Day 6**：
   - 添加更多格式化选项
   - 增强参数提取能力
   - 优化缓存机制

2. **Day 7**：
   - 性能测试和优化
   - 编写使用指南
   - 培训和交接

## 四、预期收益

### 4.1 代码质量提升

- **代码重复率降低80%**：公共逻辑全部抽取
- **测试覆盖率提升到90%**：模块化便于单元测试
- **维护成本降低60%**：修改一处即可生效

### 4.2 开发效率提升

- **新功能开发时间减少50%**：复用现有模块
- **Bug修复时间减少70%**：问题定位更精确
- **代码审查时间减少40%**：结构清晰易懂

### 4.3 系统性能提升

- **查询响应时间减少30%**：优化的参数提取和验证
- **错误处理时间减少50%**：统一的错误路径
- **内存使用减少20%**：避免重复创建对象

## 五、风险与对策

### 5.1 潜在风险

1. **兼容性风险**：新模块可能与现有代码不兼容
2. **性能风险**：模块化可能带来额外开销
3. **学习成本**：开发人员需要适应新架构

### 5.2 应对策略

1. **渐进式重构**：逐步替换，保持功能稳定
2. **性能监控**：实时监控关键指标
3. **详细文档**：提供完整的使用说明和示例
4. **充分测试**：每个阶段都进行完整测试

## 六、总结

本模块化重构方案旨在解决当前系统中的代码重复、维护困难和扩展性差等问题。通过创建一系列职责单一、接口清晰的公共模块，我们可以显著提升代码质量、开发效率和系统性能。

重构将分三个阶段进行，预计总耗时7个工作日。完成后，系统将具有更好的可维护性、可扩展性和可测试性，为未来的功能开发奠定坚实基础。