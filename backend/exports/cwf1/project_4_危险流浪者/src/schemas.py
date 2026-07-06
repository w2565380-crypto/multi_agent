from pydantic import BaseModel, validator
from typing import Optional

class CalculateRequest(BaseModel):
    """计算请求模型"""
    firstOperand: float
    secondOperand: float
    operator: str

    @validator('operator')
    def validate_operator(cls, v):
        """验证运算符是否合法"""
        valid_operators = {'+', '-', '*', '/'}
        if v not in valid_operators:
            raise ValueError(f'Invalid operator: {v}. Must be one of {valid_operators}')
        return v

class CalculateResponse(BaseModel):
    """计算响应模型"""
    result: Optional[float] = None
    error: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "result": 42.0,
                "error": None
            }
        }