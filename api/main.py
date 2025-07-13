# 文件路径: E:\PycharmProjects\stock_analysis_system\api\main.py

"""
FastAPI主接口 - 提供REST API和WebSocket服务
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import json
import asyncio
from datetime import datetime, timedelta
import uuid

from agents.hybrid_agent import HybridAgent
from database.mysql_connector import MySQLConnector
from database.milvus_connector import MilvusConnector
from config.settings import settings
from utils.logger import setup_logger


# 时间戳生成函数（替代lambda，解决OpenAPI序列化问题）
def generate_timestamp() -> str:
    """生成当前时间的ISO格式字符串"""
    return datetime.now().isoformat()


# 创建FastAPI应用
app = FastAPI(
    title="股票分析智能查询系统（旧版）",
    description="""⚠️ **废弃警告**: 此API已被废弃，请迁移到端口8001的模块化API
    
    🆕 **v2.3.0更新**: 模块化API已完全稳定，建议立即迁移
    🔄 **迁移指南**: /docs/MIGRATION_GUIDE.md
    📅 **废弃时间线**: 将在v2.4.0（2025年10月）完全移除
    ⏰ **剩余时间**: 约3个月
    
基于LangChain + RAG + 深度财务分析 + 智能日期解析 + 资金流向分析的智能股票分析API (v2.1.18)
    
## 核心功能
- 🧠 **智能查询路由**: 自动识别问题类型并路由到合适的处理模块
- 📊 **SQL数据查询**: 股价、市值、财务指标等结构化数据查询
- 📖 **RAG文档检索**: 语义搜索公告、年报、研报等文档内容
- 💰 **专业财务分析**: 四表联合分析、财务健康度评分、杜邦分析、现金流质量
- 💸 **资金流向分析**: 主力资金、超大单行为、四级资金分布分析
- 📅 **智能日期解析**: 自动识别"最新"、"最近"等时间表达
- 🌐 **网页版前端**: ChatGPT风格的自然语言交互界面
- ⚡ **WebSocket支持**: 实时对话体验
    
## 数据源
- MySQL: 2800万+条股票数据 (Tushare)
- Milvus: 120万+文档向量 (公告、年报)
- 实时资金流向数据 (tu_moneyflow_dc表)
    """,
    version="2.1.1",
    contact={
        "name": "股票分析系统",
        "url": "http://localhost:8000"
    },
    license_info={
        "name": "MIT",
    },
    tags_metadata=[
        {
            "name": "基础",
            "description": "🛠️ 基础API信息和系统状态检查"
        },
        {
            "name": "核心查询",
            "description": "🧠 智能查询路由和公司对比分析 - 最常用的API"
        },
        {
            "name": "专业财务分析",
            "description": "💰 Phase 1核心功能 - 四表联合深度财务分析、财务健康度评分、杜邦分析、现金流质量分析"
        },
        {
            "name": "资金流向分析",
            "description": "💸 Phase 2重点功能 - 主力资金、超大单行为模式识别、四级资金分布分析"
        },
        {
            "name": "数据查询",
            "description": "📊 原始数据查询 - 公司列表、最近报告等结构化数据"
        },
        {
            "name": "系统",
            "description": "💻 系统状态和监控 - 运维和调试用"
        },
        {
            "name": "辅助功能",
            "description": "💡 查询建议和智能提示"
        },
        {
            "name": "前端",
            "description": "🌐 网页版前端界面访问"
        },
        {
            "name": "高级功能",
            "description": "⚡ 流式查询和WebSocket实时通信"
        }
    ]
)

# 配置静态文件和模板
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化日志
logger = setup_logger("api")

# 全局代理实例（使用依赖注入会更好）
hybrid_agent = None
mysql_conn = None
milvus_conn = None


# 请求/响应模型
class QueryRequest(BaseModel):
    """智能查询请求模型
    
    用于封装用户的查询请求，支持上下文和过滤条件。
    """
    question: str = Field(
        ..., 
        description="用户问题，支持自然语言输入",
        example="贵州茅台最新的财务健康状况如何？"
    )
    context: Optional[Dict[str, Any]] = Field(
        None, 
        description="可选的上下文信息，用于持续对话"
    )
    filters: Optional[Dict[str, Any]] = Field(
        None, 
        description="可选的过滤条件，如股票代码、时间范围等"
    )
    top_k: Optional[int] = Field(
        5, 
        description="RAG查询返回结果数量，默认5条",
        ge=1,
        le=20
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "贵州茅台2024年第一季度的营收情况如何？",
                "context": {
                    "previous_query": "上一次查询内容",
                    "user_preference": "用户偏好设置"
                },
                "filters": {
                    "ts_code": "600519.SH",
                    "start_date": "20240101",
                    "end_date": "20240331"
                },
                "top_k": 5
            }
        }


class QueryResponse(BaseModel):
    """智能查询响应模型
    
    标准化的查询响应格式，包含结果、源数据和元数据。
    """
    success: bool = Field(
        description="查询是否成功",
        example=True
    )
    question: str = Field(
        description="用户原始问题",
        example="贵州茅台最新股价"
    )
    answer: Optional[str] = Field(
        None,
        description="智能分析结果，包含数据和分析解读",
        example="贵州茅台（600519.SH）在2025年6月20日的股价为：开盘价1423.58元..."
    )
    query_type: Optional[str] = Field(
        None,
        description="查询类型：sql/rag/financial_analysis/money_flow/hybrid",
        example="sql"
    )
    sources: Optional[Dict[str, Any]] = Field(
        None,
        description="数据源信息和元数据"
    )
    error: Optional[str] = Field(
        None,
        description="错误信息（仅在success=false时存在）"
    )
    query_id: Optional[str] = Field(
        None,
        description="查询唯一标识符，用于追踪和调试"
    )
    timestamp: str = Field(
        default_factory=generate_timestamp,
        description="响应时间戳 (ISO 8601格式)"
    )


class CompareRequest(BaseModel):
    """比较请求模型"""
    companies: List[str] = Field(..., description="公司代码列表")
    aspect: str = Field("综合表现", description="比较维度")
    period: Optional[str] = Field(None, description="时间段")
    
    class Config:
        json_schema_extra = {
            "example": {
                "companies": ["600519.SH", "000858.SZ"],
                "aspect": "盈利能力",
                "period": "2024Q1"
            },
            "examples": [
                {
                    "companies": ["600519.SH", "000858.SZ"],
                    "aspect": "盈利能力",
                    "period": "2024Q1"
                },
                {
                    "companies": ["600519.SH", "002415.SZ", "000568.SZ"],
                    "aspect": "成长能力",
                    "period": "2024年"
                }
            ]
        }


class FinancialAnalysisRequest(BaseModel):
    """财务分析请求模型"""
    ts_code: str = Field(..., description="股票代码")
    analysis_type: str = Field("financial_health", description="分析类型")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ts_code": "600519.SH",
                "analysis_type": "financial_health"
            },
            "examples": [
                {
                    "ts_code": "600519.SH",
                    "analysis_type": "financial_health"
                },
                {
                    "ts_code": "000001.SZ",
                    "analysis_type": "dupont_analysis"
                },
                {
                    "ts_code": "000002.SZ",
                    "analysis_type": "cash_flow_quality"
                }
            ]
        }


class FinancialAnalysisResponse(BaseModel):
    """财务分析响应模型"""
    success: bool
    ts_code: str
    analysis_type: str
    analysis_report: Optional[str] = None
    financial_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None
    timestamp: str = Field(default_factory=generate_timestamp)


class MoneyFlowAnalysisRequest(BaseModel):
    """资金流向分析请求模型"""
    ts_code: str = Field(..., description="股票代码")
    days: int = Field(30, description="分析天数", ge=1, le=365)
    
    class Config:
        json_schema_extra = {
            "example": {
                "ts_code": "600519.SH",
                "days": 30
            },
            "examples": [
                {
                    "ts_code": "600519.SH",
                    "days": 30
                },
                {
                    "ts_code": "000001.SZ",
                    "days": 7
                },
                {
                    "ts_code": "000002.SZ",
                    "days": 90
                }
            ]
        }


class MoneyFlowAnalysisResponse(BaseModel):
    """资金流向分析响应模型"""
    success: bool
    ts_code: str
    analysis_period: int
    analysis_report: Optional[str] = None
    money_flow_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None
    timestamp: str = Field(default_factory=generate_timestamp)


class SystemStatus(BaseModel):
    """系统状态信息模型
    
    提供系统整体运行状态和数据统计信息。
    """
    status: str = Field(
        description="系统整体状态",
        example="operational"
    )
    mysql_connected: bool = Field(
        description="MySQL数据库连接状态",
        example=True
    )
    milvus_connected: bool = Field(
        description="Milvus向量数据库连接状态",
        example=True
    )
    documents_count: int = Field(
        description="Milvus中的文档向量数量",
        example=1200000
    )
    processed_companies: int = Field(
        description="已处理的上市公司数量",
        example=5000
    )
    last_update: Optional[str] = Field(
        description="最后更新时间 (ISO 8601格式)"
    )
    websocket_connections: Optional[int] = Field(
        0,
        description="当前WebSocket活跃连接数"
    )
    websocket_stats: Optional[Dict[str, Any]] = Field(
        None,
        description="WebSocket连接详细统计"
    )


# WebSocket连接管理器
class ConnectionManager:
    """WebSocket连接管理器
    
    管理多个WebSocket连接，提供连接生命周期管理、消息发送和广播功能。
    重点关注稳定性和可靠性。
    """
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """建立WebSocket连接"""
        try:
            await websocket.accept()
            self.active_connections[client_id] = websocket
            self.user_sessions[client_id] = {
                "connected_at": datetime.now(),
                "query_count": 0,
                "last_activity": datetime.now()
            }
            logger.info(f"客户端 {client_id} 已连接")
        except Exception as e:
            logger.error(f"WebSocket连接失败 {client_id}: {e}")
            raise
    
    def disconnect(self, client_id: str):
        """断开WebSocket连接并清理资源"""
        try:
            if client_id in self.active_connections:
                del self.active_connections[client_id]
            if client_id in self.user_sessions:
                session_duration = datetime.now() - self.user_sessions[client_id]["connected_at"]
                logger.info(f"客户端 {client_id} 断开连接，会话时长: {session_duration}")
                del self.user_sessions[client_id]
        except Exception as e:
            logger.error(f"断开连接时出错 {client_id}: {e}")
    
    async def send_personal_message(self, message: str, client_id: str):
        """发送个人消息（增强错误处理）"""
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_text(message)
                # 更新活动时间
                if client_id in self.user_sessions:
                    self.user_sessions[client_id]["last_activity"] = datetime.now()
            except Exception as e:
                logger.error(f"发送消息失败 {client_id}: {e}")
                # 连接已断开，清理资源
                self.disconnect(client_id)
                raise
    
    async def broadcast(self, message: str):
        """广播消息给所有连接的客户端"""
        disconnected_clients = []
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"广播消息失败 {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # 清理断开的连接
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """获取连接统计信息"""
        return {
            "active_connections": len(self.active_connections),
            "total_queries": sum(session.get("query_count", 0) for session in self.user_sessions.values()),
            "connection_details": {
                client_id: {
                    "connected_at": session["connected_at"].isoformat(),
                    "query_count": session["query_count"],
                    "last_activity": session["last_activity"].isoformat()
                }
                for client_id, session in self.user_sessions.items()
            }
        }


manager = ConnectionManager()


# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    global hybrid_agent, mysql_conn, milvus_conn
    
    logger.info("正在初始化系统...")
    
    try:
        # 初始化连接
        mysql_conn = MySQLConnector()
        milvus_conn = MilvusConnector()
        hybrid_agent = HybridAgent()
        
        logger.info("系统初始化完成")
    except Exception as e:
        logger.error(f"系统初始化失败: {e}")
        raise


# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理"""
    global mysql_conn, milvus_conn
    
    logger.info("正在关闭系统...")
    
    if mysql_conn:
        mysql_conn.close()
    if milvus_conn:
        milvus_conn.close()
    
    logger.info("系统已关闭")


# 前端路由
@app.get("/", response_class=HTMLResponse, tags=["前端"])
async def frontend_home(request: Request):
    """前端主页"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/chat", response_class=HTMLResponse, tags=["前端"])
async def frontend_chat(request: Request):
    """聊天界面（重定向到主页）"""
    return templates.TemplateResponse("index.html", {"request": request})


# API信息路由
@app.get("/api", tags=["基础"])
async def api_info():
    """获取API基本信息和功能列表
    
    返回系统版本、功能特性、访问地址等基本信息。
    """
    return {
        "message": "股票分析智能查询系统 API",
        "version": "1.4.1",
        "release_date": "2025-06-23",
        "features": [
            "🧠 智能查询路由 - 自动识别问题类型",
            "📊 SQL数据查询 - 股价、财务指标查询",
            "📖 RAG文档检索 - 语义搜索年报公告", 
            "💰 专业财务分析 - 四表联合深度分析",
            "📈 财务健康度评分 - AAA-CCC专业评级",
            "🔍 杜邦分析 - ROE三因素分解",
            "💧 现金流质量分析 - A-D级质量评估",
            "📅 智能日期解析 - 自动识别时间表达",
            "💸 资金流向分析 - 主力资金行为追踪",
            "💰 超大单分析 - 机构行为模式识别",
            "📊 四级资金分布 - 全方位资金结构",
            "🌐 网页版前端界面 - ChatGPT式交互",
            "⚡ WebSocket实时通信 - 即时对话体验"
        ],
        "endpoints": {
            "frontend": "/",
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "status": "/status"
        },
        "data_stats": {
            "mysql_records": "28M+ 股票数据记录",
            "milvus_documents": "120万+ 文档向量",
            "companies_covered": "5000+ 上市公司",
            "data_sources": ["Tushare", "东方财富", "巨潮资讯"]
        }
    }


@app.get("/health", tags=["基础"])
async def health_check():
    """系统健康状态检查
    
    检查MySQL和Milvus数据库连接状态，返回系统整体健康度。
    用于监控和运维，确保系统正常运行。
    
    Returns:
        dict: 包含系统状态、数据库连接状态和时间戳的健康检查结果
    """
    try:
        # 检查数据库连接
        mysql_ok = mysql_conn.test_connection() if mysql_conn else False
        milvus_stats = milvus_conn.get_collection_stats() if milvus_conn else {}
        
        return {
            "status": "healthy" if mysql_ok else "unhealthy",
            "services": {
                "mysql": "✅ 连接正常" if mysql_ok else "❌ 连接异常",
                "milvus": "✅ 连接正常" if bool(milvus_stats) else "❌ 连接异常",
                "hybrid_agent": "✅ 就绪" if hybrid_agent else "❌ 未初始化"
            },
            "database_stats": {
                "mysql_connected": mysql_ok,
                "milvus_connected": bool(milvus_stats),
                "milvus_document_count": milvus_stats.get('row_count', 0) if milvus_stats else 0
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy", 
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@app.get("/status", response_model=SystemStatus, tags=["系统"])
async def get_system_status():
    """获取系统状态"""
    try:
        # 获取系统状态
        mysql_ok = mysql_conn.test_connection() if mysql_conn else False
        milvus_stats = milvus_conn.get_collection_stats() if milvus_conn else {}
        
        # 获取已处理公司数
        processed_companies = 0
        if milvus_conn:
            try:
                results = milvus_conn.collection.query(
                    expr="chunk_id == 0",
                    output_fields=["ts_code"],
                    limit=10000
                )
                unique_companies = set(r.get('ts_code', '') for r in results)
                processed_companies = len(unique_companies)
            except:
                pass
        
        # 获取WebSocket连接统计
        websocket_stats = manager.get_connection_stats()
        
        return SystemStatus(
            status="operational",
            mysql_connected=mysql_ok,
            milvus_connected=bool(milvus_stats),
            documents_count=milvus_stats.get('row_count', 0),
            processed_companies=processed_companies,
            last_update=datetime.now().isoformat(),
            websocket_connections=websocket_stats["active_connections"],
            websocket_stats=websocket_stats
        )
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse, tags=["核心查询"])
async def query(request: QueryRequest):
    """智能查询接口 - 核心功能
    
    自动识别用户问题类型并路由到合适的处理模块：
    - SQL查询：股价、市值、财务指标等数值类问题
    - RAG查询：公告内容、年报分析等文本类问题  
    - 财务分析：财务健康度、杜邦分析等专业分析
    - 资金流向：主力资金、超大单行为等资金分析
    - 混合查询：需要多种数据源的复杂问题
    
    支持自然语言输入，如：
    - "贵州茅台最新股价"
    - "分析茅台的财务健康状况"
    - "茅台的资金流向如何"
    - "茅台最新年报说了什么"
    """
    query_id = str(uuid.uuid4())
    logger.info(f"收到查询请求 {query_id}: {request.question}")
    
    try:
        if not hybrid_agent:
            raise HTTPException(status_code=503, detail="系统未初始化")
        
        # 执行查询
        result = hybrid_agent.query(
            question=request.question,
            context=request.context
        )
        
        # 构建响应
        response = QueryResponse(
            success=result.get('success', False),
            question=request.question,
            answer=result.get('answer'),
            query_type=result.get('query_type'),
            sources=result.get('sources'),
            error=result.get('error'),
            query_id=query_id
        )
        
        logger.info(f"查询 {query_id} 完成: {response.success}")
        return response
        
    except Exception as e:
        logger.error(f"查询 {query_id} 失败: {e}")
        return QueryResponse(
            success=False,
            question=request.question,
            error=str(e),
            query_id=query_id
        )


@app.post("/compare", tags=["核心查询"])
async def compare_companies(request: CompareRequest):
    """多公司对比分析
    
    支持2家或多家公司的对比分析，可指定对比维度和时间段。
    
    对比维度支持：
    - 综合表现：整体财务和市场表现对比
    - 盈利能力：ROE、净利率、毛利率等对比
    - 偿债能力：资产负债率、流动比率等对比
    - 成长能力：营收增长、利润增长等对比
    - 估值水平：PE、PB、PEG等估值指标对比
    
    示例：
    - 比较贵州茅台和五粮液的盈利能力
    - 对比平安银行和招商银行2024Q1表现
    """
    try:
        if not hybrid_agent:
            raise HTTPException(status_code=503, detail="系统未初始化")
        
        # 构建比较查询
        if len(request.companies) == 2:
            question = f"比较{request.companies[0]}和{request.companies[1]}的{request.aspect}"
        else:
            question = f"比较以下公司的{request.aspect}：" + "、".join(request.companies)
        
        if request.period:
            question += f"（{request.period}）"
        
        # 执行查询
        result = hybrid_agent.query(question)
        
        return {
            "success": result.get('success', False),
            "companies": request.companies,
            "aspect": request.aspect,
            "period": request.period,
            "comparison": result.get('answer'),
            "sources": result.get('sources')
        }
        
    except Exception as e:
        logger.error(f"公司比较失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/suggestions", tags=["辅助功能"])
async def get_query_suggestions(q: str = Query(..., description="用户输入")):
    """智能查询建议
    
    基于用户输入内容，提供相关的查询建议，帮助用户发现更多分析角度。
    
    功能特点：
    - 根据股票名称/代码提供针对性建议
    - 涵盖财务分析、资金流向、公告查询等多个维度
    - 智能匹配用户可能感兴趣的查询方向
    
    Args:
        q: 用户输入的查询内容或股票名称
        
    Returns:
        dict: 包含建议查询列表的响应
    """
    try:
        # 简单的建议生成
        suggestions = []
        
        # 基于输入生成建议
        if "茅台" in q or "600519" in q:
            suggestions.extend([
                "贵州茅台最新财报分析",
                "贵州茅台2024年营收情况",
                "贵州茅台与五粮液对比",
                "贵州茅台的投资价值分析"
            ])
        
        # 通用建议
        suggestions.extend([
            f"{q}的财务表现如何？",
            f"{q}最新公告说了什么？",
            f"分析{q}的投资机会",
            f"{q}的行业地位如何？"
        ])
        
        return {"suggestions": suggestions[:5]}
        
    except Exception as e:
        logger.error(f"生成建议失败: {e}")
        return {"suggestions": []}


@app.post("/financial-analysis", response_model=FinancialAnalysisResponse, tags=["专业财务分析"])
async def financial_analysis(request: FinancialAnalysisRequest):
    """专业财务分析接口 - Phase 1 核心功能
    
    基于四表联合分析（利润表83字段 + 资产负债表161字段 + 现金流量表73字段 + 财务指标143字段）
    提供专业级财务分析报告。
    
    支持的分析类型：
    - **financial_health**: 财务健康度评分 (AAA-CCC评级)
      - 盈利能力 (30%): ROE、净利率、毛利率
      - 偿债能力 (25%): 资产负债率、流动比率、速动比率
      - 运营能力 (25%): 资产周转率、存货周转率等
      - 成长能力 (20%): 营收增长率、净利润增长率等
    
    - **dupont_analysis**: 杜邦分析
      - ROE = 净利率 × 总资产周转率 × 权益乘数
      - 支持多期趋势分析和同行业对比
    
    - **cash_flow_quality**: 现金流质量分析
      - 现金含量比率 = 经营现金流 / 净利润
      - A-D级质量评级和风险提示
    
    - **multi_period_comparison**: 多期财务对比
      - 同比/环比增长率分析
      - 趋势变化和波动性评估
    
    分析结果包含：
    - 📊 专业财务评分和评级
    - 🔍 详细的财务指标分析
    - ⚠️ 风险提示和投资建议
    - 📈 LLM增强的专业解读
    """
    import time
    
    try:
        if not hybrid_agent:
            raise HTTPException(status_code=503, detail="系统未初始化")
        
        # 构建财务分析查询
        analysis_queries = {
            "financial_health": f"分析{request.ts_code}的财务健康状况",
            "dupont_analysis": f"对{request.ts_code}进行杜邦分析",
            "cash_flow_quality": f"分析{request.ts_code}的现金流质量",
            "multi_period_comparison": f"{request.ts_code}的多期财务对比分析"
        }
        
        query_text = analysis_queries.get(request.analysis_type, 
                                         f"分析{request.ts_code}的财务状况")
        
        # 执行财务分析
        start_time = time.time()
        result = hybrid_agent.query(query_text)
        processing_time = time.time() - start_time
        
        if result.get('success', False):
            return FinancialAnalysisResponse(
                success=True,
                ts_code=request.ts_code,
                analysis_type=request.analysis_type,
                analysis_report=result.get('answer'),
                financial_data=result.get('financial_data'),
                processing_time=processing_time
            )
        else:
            return FinancialAnalysisResponse(
                success=False,
                ts_code=request.ts_code,
                analysis_type=request.analysis_type,
                error=result.get('error', '财务分析失败'),
                processing_time=processing_time
            )
        
    except Exception as e:
        logger.error(f"财务分析API失败: {e}")
        return FinancialAnalysisResponse(
            success=False,
            ts_code=request.ts_code,
            analysis_type=request.analysis_type,
            error=str(e)
        )


@app.post("/money-flow-analysis", response_model=MoneyFlowAnalysisResponse, tags=["资金流向分析"])
async def money_flow_analysis(request: MoneyFlowAnalysisRequest):
    """资金流向分析接口 - Phase 2 重点功能
    
    基于tu_moneyflow_dc表数据，提供专业级资金流向分析报告。
    
    核心分析维度：
    
    **1. 主力资金分析 (最高优先级)**
    - 主力资金 = 大单(20-100万) + 超大单(≥100万)
    - 净流入/流出金额和趋势分析
    - 流向强度评估：强势(>5000万)/中等(1000-5000万)/弱势(<1000万)
    - 流向一致性评分(0-100%)
    
    **2. 超大单资金分析 (重点单独分析)**
    - 超大单(≥100万)行为模式识别：
      - 📈 建仓模式：买入占比>65%且净流入为正
      - 📉 减仓模式：买入占比<35%且净流出为负
      - 🔄 洗盘模式：买卖相当，净流向接近0
      - ❓ 不明模式：其他情况
    - 机构资金主导程度分析
    - 与股价走势的相关性分析
    
    **3. 四级资金分布分析**
    - 超大单：≥100万元 (机构资金)
    - 大单：20-100万元 (大户资金)
    - 中单：4-20万元 (中户资金)
    - 小单：<4万元 (散户资金)
    - 各级别资金占比和流向趋势
    
    **4. 综合评估和投资建议**
    - 基于资金流向的整体评估
    - 风险提示和投资建议
    - LLM增强的专业解读
    
    分析结果包含：
    - 💰 主力资金净流向及强度评估
    - 📈 超大单机构行为模式识别
    - 📊 四级资金的分布情况和趋势
    - ⚠️ 风险警示和投资策略建议
    
    示例查询：
    - 分析贵州茅台最近30天的资金流向
    - 查看平安银行的主力资金流入情况
    - 茅台的超大单资金如何
    """
    import time
    
    try:
        if not hybrid_agent:
            raise HTTPException(status_code=503, detail="系统未初始化")
        
        # 构建资金流向分析查询
        query_text = f"分析{request.ts_code}最近{request.days}天的资金流向"
        
        # 执行资金流向分析
        start_time = time.time()
        result = hybrid_agent.query(query_text)
        processing_time = time.time() - start_time
        
        if result.get('success', False):
            return MoneyFlowAnalysisResponse(
                success=True,
                ts_code=request.ts_code,
                analysis_period=request.days,
                analysis_report=result.get('answer'),
                money_flow_data=result.get('money_flow_data'),
                processing_time=processing_time
            )
        else:
            return MoneyFlowAnalysisResponse(
                success=False,
                ts_code=request.ts_code,
                analysis_period=request.days,
                error=result.get('error', '资金流向分析失败'),
                processing_time=processing_time
            )
        
    except Exception as e:
        logger.error(f"资金流向分析API失败: {e}")
        return MoneyFlowAnalysisResponse(
            success=False,
            ts_code=request.ts_code,
            analysis_period=request.days,
            error=str(e)
        )


@app.get("/companies", tags=["数据查询"])
async def list_companies(
    sector: Optional[str] = None,
    limit: int = Query(20, le=100)
):
    """获取上市公司列表
    
    查询数据库中的上市公司信息，支持按行业过滤。
    
    Args:
        sector: 可选，按行业过滤 (如："白酒行业"、"银行业"等)
        limit: 返回结果数量限制，最大100
        
    Returns:
        dict: 包含公司代码、名称等信息的公司列表
        
    示例：
    - 获取所有公司前20家
    - 获取白酒行业所有公司
    """
    try:
        # 构建查询
        query = "SELECT DISTINCT ts_code, name FROM stock_basic"
        if sector:
            query += f" WHERE industry = '{sector}'"
        query += f" LIMIT {limit}"
        
        companies = mysql_conn.execute_query(query)
        
        return {
            "total": len(companies),
            "companies": companies
        }
        
    except Exception as e:
        logger.error(f"获取公司列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reports/recent", tags=["数据查询"])
async def get_recent_reports(days: int = 7, limit: int = 20):
    """获取最近发布的财务报告
    
    查询指定时间范围内发布的年度报告和季度报告信息。
    
    Args:
        days: 查询范围（天数），默认查询近7天
        limit: 返回结果数量限制，默认20条
        
    Returns:
        dict: 包含报告时间范围、总数量和报告列表
        
    报告信息包含：
    - 股票代码和公司名称
    - 报告标题和发布日期
    - 报告下载链接
    """
    try:
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        query = f"""
        SELECT ts_code, name, title, ann_date, url
        FROM tu_anns_d
        WHERE ann_date BETWEEN '{start_date}' AND '{end_date}'
        AND (title LIKE '%年度报告%' OR title LIKE '%季度报告%')
        ORDER BY ann_date DESC
        LIMIT {limit}
        """
        
        reports = mysql_conn.execute_query(query)
        
        return {
            "period": {"start": start_date, "end": end_date},
            "total": len(reports),
            "reports": reports
        }
        
    except Exception as e:
        logger.error(f"获取最近报告失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket路由
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket实时通信端点
    
    提供WebSocket实时双向通信，支持即时查询和结果推送。
    主要用于网页版前端的实时交互。
    
    支持的消息类型：
    - **query**: 执行智能查询
      ```json
      {
          "type": "query",
          "question": "贵州茅台最新股价"
      }
      ```
    
    - **ping**: 心跳检测
      ```json
      {
          "type": "ping"
      }
      ```
    
    连接特性：
    - 自动分配唯一客户端ID
    - 支持多客户端并发连接
    - 断线自动清理资源
    - 增强错误处理和稳定性保障
    """
    client_id = str(uuid.uuid4())
    
    try:
        await manager.connect(websocket, client_id)
        
        # 发送欢迎消息
        await manager.send_personal_message(
            json.dumps({
                "type": "welcome",
                "message": "WebSocket连接成功，可以开始查询",
                "client_id": client_id,
                "timestamp": datetime.now().isoformat()
            }),
            client_id
        )
        
        while True:
            try:
                # 接收消息
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # 更新查询计数
                if client_id in manager.user_sessions:
                    manager.user_sessions[client_id]["query_count"] += 1
                
                # 处理不同类型的消息
                if message.get("type") == "query":
                    # 执行查询
                    query_id = str(uuid.uuid4())
                    question = message.get("question", "").strip()
                    
                    if not question:
                        await manager.send_personal_message(
                            json.dumps({
                                "type": "error",
                                "error": "查询内容不能为空",
                                "query_id": query_id
                            }),
                            client_id
                        )
                        continue
                    
                    # 发送处理中消息
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "processing",
                            "query_id": query_id,
                            "message": "正在处理您的查询..."
                        }),
                        client_id
                    )
                    
                    try:
                        # 执行查询
                        result = hybrid_agent.query(question)
                        
                        # 发送结果
                        await manager.send_personal_message(
                            json.dumps({
                                "type": "analysis_result",
                                "query_id": query_id,
                                "content": result,
                                "timestamp": datetime.now().isoformat()
                            }),
                            client_id
                        )
                        
                    except Exception as e:
                        logger.error(f"查询执行失败 {client_id}: {e}")
                        await manager.send_personal_message(
                            json.dumps({
                                "type": "error",
                                "query_id": query_id,
                                "error": f"查询执行失败: {str(e)}"
                            }),
                            client_id
                        )
                
                elif message.get("type") == "ping":
                    # 心跳检测响应
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "pong",
                            "timestamp": datetime.now().isoformat()
                        }),
                        client_id
                    )
                
                else:
                    # 未知消息类型
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "error",
                            "error": f"未知消息类型: {message.get('type')}"
                        }),
                        client_id
                    )
                    
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    json.dumps({
                        "type": "error",
                        "error": "消息格式错误，请发送有效的JSON"
                    }),
                    client_id
                )
            except Exception as e:
                logger.error(f"WebSocket消息处理错误 {client_id}: {e}")
                break
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"WebSocket客户端 {client_id} 主动断开连接")
    except Exception as e:
        logger.error(f"WebSocket错误 {client_id}: {e}")
        manager.disconnect(client_id)


# 流式响应端点（用于大型查询）
@app.post("/query/stream", tags=["高级功能"])
async def query_stream(request: QueryRequest):
    """流式查询响应 - 适用于大型查询
    
    为大型复杂查询提供流式响应，实时返回部分结果，提升用户体验。
    特别适用于财务分析、资金流向分析等耗时较长的查询。
    
    响应格式：application/x-ndjson (新行分隔JSON)
    
    流式消息类型：
    - **start**: 查询开始信息
      ```json
      {
          "type": "start",
          "query_id": "uuid",
          "timestamp": "2025-06-23T10:00:00Z"
      }
      ```
    
    - **chunk**: 部分结果块
      ```json
      {
          "type": "chunk",
          "content": "查询结果的一部分..."
      }
      ```
    
    - **complete**: 查询完成信息
      ```json
      {
          "type": "complete",
          "query_id": "uuid",
          "sources": {}
      }
      ```
    
    - **error**: 错误信息
      ```json
      {
          "type": "error",
          "error": "错误描述"
      }
      ```
    
    使用场景：
    - 复杂财务分析报告生成
    - 多公司对比分析
    - 大量数据的资金流向分析
    """
    query_id = str(uuid.uuid4())
    
    async def generate():
        try:
            # 发送开始消息
            yield json.dumps({
                "type": "start",
                "query_id": query_id,
                "timestamp": datetime.now().isoformat()
            }) + "\n"
            
            # 执行查询（这里应该改为流式处理）
            result = hybrid_agent.query(request.question)
            
            # 模拟流式输出
            if result.get("success") and result.get("answer"):
                answer = result["answer"]
                # 分段发送
                chunk_size = 50
                for i in range(0, len(answer), chunk_size):
                    chunk = answer[i:i+chunk_size]
                    yield json.dumps({
                        "type": "chunk",
                        "content": chunk
                    }) + "\n"
                    await asyncio.sleep(0.1)  # 模拟延迟
            
            # 发送完成消息
            yield json.dumps({
                "type": "complete",
                "query_id": query_id,
                "sources": result.get("sources", {})
            }) + "\n"
            
        except Exception as e:
            yield json.dumps({
                "type": "error",
                "error": str(e)
            }) + "\n"
    
    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson"
    )


if __name__ == "__main__":
    import uvicorn
    
    # 运行服务器
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )