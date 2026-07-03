/**
 * api.js - 封装与后端的 HTTP 通信
 * 注意：本计算器演示版本中，计算逻辑完全在前端执行，无需后端。
 * 但为遵循架构设计，保留此模块，并实现一个本地计算函数作为 fallback。
 * 若后端可用，可取消注释 fetch 部分并配置 BASE_URL。
 */

const API_BASE_URL = 'http://localhost:8000'; // 后端地址，按需修改

/**
 * 调用后端计算 API
 * @param {number} firstOperand
 * @param {number} secondOperand
 * @param {string} operator - '+', '-', '*', '/'
 * @returns {Promise<{result?: number, error?: string}>}
 */
async function calculateRemote(firstOperand, secondOperand, operator) {
    // 如果后端不可用，回退到本地计算
    // 这里为了演示，直接调用本地计算，避免网络依赖
    // 实际项目中可启用以下 fetch 代码
    /*
    try {
        const response = await fetch(`${API_BASE_URL}/api/calculate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ firstOperand, secondOperand, operator }),
        });
        if (!response.ok) {
            const errorData = await response.json();
            return { error: errorData.error || '请求失败' };
        }
        return await response.json();
    } catch (error) {
        console.error('API 请求失败，使用本地计算:', error);
        return calculateLocal(firstOperand, secondOperand, operator);
    }
    */
    // 默认使用本地计算
    return calculateLocal(firstOperand, secondOperand, operator);
}

/**
 * 本地计算函数（纯前端实现）
 * @param {number} a
 * @param {number} b
 * @param {string} operator
 * @returns {{result?: number, error?: string}}
 */
function calculateLocal(a, b, operator) {
    let result;
    switch (operator) {
        case '+':
            result = a + b;
            break;
        case '-':
            result = a - b;
            break;
        case '*':
            result = a * b;
            break;
        case '/':
            if (b === 0) {
                return { error: 'Division by zero' };
            }
            result = a / b;
            break;
        default:
            return { error: 'Invalid operator' };
    }

    // 处理溢出或非数字
    if (!isFinite(result)) {
        if (result === Infinity || result === -Infinity) {
            return { error: 'Infinity' };
        }
        return { error: 'NaN' };
    }

    // 限制显示精度，避免浮点误差
    // 保留最多 10 位小数
    if (Number.isInteger(result)) {
        return { result };
    } else {
        return { result: parseFloat(result.toPrecision(12)) };
    }
}

/**
 * 全局 401 鉴权拦截（预留，本应用无鉴权）
 * 若未来增加后端鉴权，可在此处统一处理
 */
function handleUnauthorized() {
    // 清除本地存储的 token
    localStorage.removeItem('authToken');
    // 重定向到登录页
    window.location.href = '/admin/login.html';
}

// 暴露函数供 calculator.js 使用
window.calculateRemote = calculateRemote;