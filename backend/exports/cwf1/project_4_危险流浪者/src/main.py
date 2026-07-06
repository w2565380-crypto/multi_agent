import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import CalculateRequest, CalculateResponse
from calculator import calculate

app = FastAPI(
    title="Simple Calculator API",
    description="提供基本四则运算的计算服务",
    version="1.0.0"
)

# CORS 配置，允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/calculate", response_model=CalculateResponse)
async def calculate_endpoint(request: CalculateRequest):
    """
    执行四则运算
    
    - **firstOperand**: 第一个操作数
    - **secondOperand**: 第二个操作数
    - **operator**: 运算符（+、-、*、/）
    
    返回计算结果或错误信息
    """
    try:
        result = calculate(
            request.firstOperand,
            request.secondOperand,
            request.operator
        )
        return CalculateResponse(result=result)
    except ValueError as e:
        # 处理除零、溢出等业务错误
        return CalculateResponse(error=str(e))
    except Exception as e:
        # 处理未知错误
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host=host, port=port)