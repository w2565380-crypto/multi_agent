import math

def calculate(first_operand: float, second_operand: float, operator: str) -> float:
    """
    执行基本四则运算
    
    Args:
        first_operand: 第一个操作数
        second_operand: 第二个操作数
        operator: 运算符（+、-、*、/）
    
    Returns:
        计算结果
    
    Raises:
        ValueError: 当发生除零、溢出或无效结果时
    """
    # 执行运算
    if operator == '+':
        result = first_operand + second_operand
    elif operator == '-':
        result = first_operand - second_operand
    elif operator == '*':
        result = first_operand * second_operand
    elif operator == '/':
        # 检查除零
        if second_operand == 0:
            raise ValueError("Division by zero")
        result = first_operand / second_operand
    else:
        raise ValueError(f"Unsupported operator: {operator}")
    
    # 检查结果是否有效（处理溢出和NaN）
    if math.isnan(result):
        raise ValueError("NaN")
    if math.isinf(result):
        if result > 0:
            raise ValueError("Infinity")
        else:
            raise ValueError("-Infinity")
    
    # 限制精度，避免浮点数误差传播
    # 保留10位小数，避免显示过长
    result = round(result, 10)
    
    return result