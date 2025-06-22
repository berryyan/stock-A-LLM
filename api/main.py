# 文件路径: E:\PycharmProjects\stock_analysis_system\api\main.py

"""
FastAPI主接口 - 提供REST API和WebSocket服务
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
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


# 创建FastAPI应用
app = FastAPI(
    title="股票分析智能查询系统",
    description="基于LangChain + RAG + 深度财务分析的智能股票分析API (v1.4.0)",
    version="1.4.0"
)

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
    """查询请求模型"""
    question: str = Field(..., description="用户问题")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")
    filters: Optional[Dict[str, Any]] = Field(None, description="过滤条件")
    top_k: Optional[int] = Field(5, description="返回结果数量")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "贵州茅台2024年第一季度的营收情况如何？",
                "filters": {"ts_code": "600519.SH"},
                "top_k": 5
            }
        }


class QueryResponse(BaseModel):
    """查询响应模型"""
    success: bool
    question: str
    answer: Optional[str] = None
    query_type: Optional[str] = None
    sources: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    query_id: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


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
            }
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
            }
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
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class SystemStatus(BaseModel):
    """系统状态模型"""
    status: str
    mysql_connected: bool
    milvus_connected: bool
    documents_count: int
    processed_companies: int
    last_update: Optional[str]


# WebSocket连接管理器
class ConnectionManager:
    """WebSocket连接管理器"""
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.user_sessions[client_id] = {
            "connected_at": datetime.now(),
            "query_count": 0
        }
        logger.info(f"客户端 {client_id} 已连接")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            del self.user_sessions[client_id]
            logger.info(f"客户端 {client_id} 已断开")
    
    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)


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


# API路由
@app.get("/", tags=["基础"])
async def root():
    """API根路径"""
    return {
        "message": "股票分析智能查询系统 API",
        "version": "1.4.0",
        "features": [
            "智能查询路由",
            "SQL数据查询",
            "RAG文档检索", 
            "专业财务分析",
            "四表联合分析",
            "财务健康度评分",
            "杜邦分析",
            "现金流质量分析"
        ],
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["基础"])
async def health_check():
    """健康检查"""
    try:
        # 检查数据库连接
        mysql_ok = mysql_conn.test_connection() if mysql_conn else False
        milvus_stats = milvus_conn.get_collection_stats() if milvus_conn else {}
        
        return {
            "status": "healthy" if mysql_ok else "unhealthy",
            "mysql": mysql_ok,
            "milvus": bool(milvus_stats),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
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
        
        return SystemStatus(
            status="operational",
            mysql_connected=mysql_ok,
            milvus_connected=bool(milvus_stats),
            documents_count=milvus_stats.get('row_count', 0),
            processed_companies=processed_companies,
            last_update=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse, tags=["查询"])
async def query(request: QueryRequest):
    """执行智能查询"""
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


@app.post("/compare", tags=["查询"])
async def compare_companies(request: CompareRequest):
    """比较多家公司"""
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


@app.get("/suggestions", tags=["查询"])
async def get_query_suggestions(q: str = Query(..., description="用户输入")):
    """获取查询建议"""
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


@app.post("/financial-analysis", response_model=FinancialAnalysisResponse, tags=["财务分析"])
async def financial_analysis(request: FinancialAnalysisRequest):
    """专业财务分析"""
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


@app.get("/companies", tags=["数据"])
async def list_companies(
    sector: Optional[str] = None,
    limit: int = Query(20, le=100)
):
    """获取公司列表"""
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


@app.get("/reports/recent", tags=["数据"])
async def get_recent_reports(days: int = 7, limit: int = 20):
    """获取最近的报告"""
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
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket连接端点"""
    await manager.connect(websocket, client_id)
    
    try:
        # 发送欢迎消息
        await manager.send_personal_message(
            json.dumps({
                "type": "welcome",
                "message": "连接成功，可以开始查询",
                "client_id": client_id
            }),
            client_id
        )
        
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理不同类型的消息
            if message.get("type") == "query":
                # 执行查询
                query_id = str(uuid.uuid4())
                
                # 发送处理中消息
                await manager.send_personal_message(
                    json.dumps({
                        "type": "processing",
                        "query_id": query_id,
                        "message": "正在处理您的查询..."
                    }),
                    client_id
                )
                
                # 执行查询
                try:
                    result = hybrid_agent.query(message.get("question", ""))
                    
                    # 发送结果
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "result",
                            "query_id": query_id,
                            "success": result.get("success", False),
                            "answer": result.get("answer"),
                            "query_type": result.get("query_type"),
                            "sources": result.get("sources")
                        }),
                        client_id
                    )
                except Exception as e:
                    # 发送错误消息
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "error",
                            "query_id": query_id,
                            "error": str(e)
                        }),
                        client_id
                    )
            
            elif message.get("type") == "ping":
                # 心跳响应
                await manager.send_personal_message(
                    json.dumps({"type": "pong"}),
                    client_id
                )
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"WebSocket客户端 {client_id} 断开连接")
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        manager.disconnect(client_id)


# 流式响应端点（用于大型查询）
@app.post("/query/stream", tags=["查询"])
async def query_stream(request: QueryRequest):
    """流式查询响应"""
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