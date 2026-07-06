// ===== 状态管理 =====
const state = {
    currentInput: '0',      // 当前输入的数字字符串
    previousOperand: null,  // 第一个操作数（数字）
    operator: null,         // 当前运算符 ('+', '-', '*', '/')
    waitingForOperand: false, // 是否正在等待第二个操作数
    justEvaluated: false,   // 刚按了等于键，准备新输入
    error: false,           // 是否处于错误状态
    expression: ''          // 上行显示的表达式字符串
};

// ===== DOM 引用 =====
const expressionEl = document.getElementById('expression');
const currentInputEl = document.getElementById('currentInput');

// ===== 工具函数 =====
function formatNumber(num) {
    // 将数字转为字符串，保留10位小数并去除末尾0
    if (typeof num !== 'number' || !isFinite(num)) {
        return '错误';
    }
    let str = num.toFixed(10);
    // 移除末尾的0，但保留至少一位小数（如果原本是小数）
    str = str.replace(/(\.\d*?)0+$/, '$1');
    if (str.endsWith('.')) {
        str = str.slice(0, -1);
    }
    return str;
}

function updateDisplay() {
    expressionEl.textContent = state.expression;
    if (state.error) {
        currentInputEl.textContent = '错误';
    } else {
        currentInputEl.textContent = state.currentInput;
    }
}

function resetState() {
    state.currentInput = '0';
    state.previousOperand = null;
    state.operator = null;
    state.waitingForOperand = false;
    state.justEvaluated = false;
    state.error = false;
    state.expression = '';
    updateDisplay();
}

// 设置错误状态
function setError() {
    state.error = true;
    state.currentInput = '错误';
    updateDisplay();
}

// ===== 数字输入 =====
function inputDigit(digit) {
    if (state.error) return;
    if (state.justEvaluated) {
        // 刚显示结果，开始新数字输入
        state.currentInput = digit;
        state.justEvaluated = false;
        state.expression = ''; // 清空上行表达式
        state.previousOperand = null;
        state.operator = null;
        state.waitingForOperand = false;
    } else if (state.waitingForOperand) {
        // 等待第二个操作数，新数字覆盖
        state.currentInput = digit;
        state.waitingForOperand = false;
    } else {
        // 正常追加
        if (state.currentInput === '0') {
            state.currentInput = digit; // 不允许前导0
        } else {
            state.currentInput += digit;
        }
    }
    updateDisplay();
}

// ===== 小数点输入 =====
function inputDecimal() {
    if (state.error) return;
    if (state.justEvaluated) {
        // 刚显示结果，自动补 '0.'
        state.currentInput = '0.';
        state.justEvaluated = false;
        state.expression = '';
        state.previousOperand = null;
        state.operator = null;
        state.waitingForOperand = false;
        updateDisplay();
        return;
    }
    if (state.waitingForOperand) {
        // 等待第二个操作数时按小数点，新输入以 '0.' 开始
        state.currentInput = '0.';
        state.waitingForOperand = false;
        updateDisplay();
        return;
    }
    // 当前输入中已有小数点则忽略
    if (state.currentInput.indexOf('.') !== -1) return;
    state.currentInput += '.';
    updateDisplay();
}

// ===== 运算符输入 =====
function handleOperator(op) {
    if (state.error) return;
    const current = parseFloat(state.currentInput);
    if (isNaN(current)) {
        setError();
        return;
    }
    if (state.justEvaluated) {
        // 刚显示结果，将结果作为第一个操作数开始新运算
        state.previousOperand = current;
        state.justEvaluated = false;
        state.waitingForOperand = true;
        state.operator = op;
        state.expression = state.currentInput + ' ' + getOperatorSymbol(op) + ' ';
        updateDisplay();
        return;
    }
    if (state.waitingForOperand) {
        // 仅替换运算符
        state.operator = op;
        // 更新上行表达式，替换运算符符号
        const parts = state.expression.trim().split(' ');
        if (parts.length >= 2) {
            parts[1] = getOperatorSymbol(op);
            state.expression = parts.join(' ') + ' ';
        } else {
            state.expression = state.currentInput + ' ' + getOperatorSymbol(op) + ' ';
        }
        updateDisplay();
        return;
    }
    // 正常情况：已有第一个操作数，需要先计算结果再开始新运算？
    // 简易计算器通常直接存储第一个操作数，然后等待第二个
    // 但如果之前已经有一个运算符未完成，应当先计算并作为新运算的开始
    if (state.operator && state.previousOperand !== null && !state.waitingForOperand) {
        // 此时有第一个数、运算符、第二个数，应立刻计算并作为新运算的第一个数
        performCalculation();
        if (state.error) return;
        state.previousOperand = parseFloat(state.currentInput);
        state.operator = op;
        state.waitingForOperand = true;
        state.justEvaluated = false;
        state.expression = state.currentInput + ' ' + getOperatorSymbol(op) + ' ';
        updateDisplay();
        return;
    }
    // 否则，当前是第一个操作数
    state.previousOperand = current;
    state.operator = op;
    state.waitingForOperand = true;
    state.justEvaluated = false;
    state.expression = state.currentInput + ' ' + getOperatorSymbol(op) + ' ';
    updateDisplay();
}

function getOperatorSymbol(op) {
    const map = { '+': '+', '-': '-', '*': '×', '/': '÷' };
    return map[op] || op;
}

// ===== 计算执行 =====
function performCalculation() {
    if (state.error) return;
    if (state.operator === null || state.previousOperand === null) return;
    const a = state.previousOperand;
    const b = parseFloat(state.currentInput);
    if (isNaN(b)) {
        setError();
        return;
    }
    let result;
    switch (state.operator) {
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
                // 除零错误，设置错误但保留表达式
                state.error = true;
                state.currentInput = '错误';
                // 保留完整表达式，包括第二个操作数
                state.expression = formatOperand(a) + ' ' + getOperatorSymbol(state.operator) + ' ' + formatOperand(b) + ' =';
                updateDisplay();
                return;
            }
            result = a / b;
            break;
        default:
            setError();
            return;
    }
    // 检查是否溢出（超出JS安全整数范围）
    if (!isFinite(result) || Math.abs(result) > Number.MAX_SAFE_INTEGER) {
        setError();
        return;
    }
    // 格式化结果
    const formatted = formatNumber(result);
    if (formatted === '错误') {
        setError();
        return;
    }
    // 保存结果到当前输入，并清除运算符等状态
    state.currentInput = formatted;
    state.previousOperand = null;
    state.operator = null;
    state.waitingForOperand = false;
    state.justEvaluated = true;
    state.error = false;
    // 更新上行表达式为完整等式
    state.expression = formatOperand(a) + ' ' + getOperatorSymbol(state.operator) + ' ' + formatOperand(b) + ' =';
    updateDisplay();
}

function formatOperand(num) {
    // 辅助格式化操作数（用于表达式显示）
    if (Number.isInteger(num)) {
        return num.toString();
    }
    return formatNumber(num);
}

// ===== 等于操作 =====
function handleEquals() {
    if (state.error) return;
    if (state.waitingForOperand && state.operator && state.previousOperand !== null) {
        // 按了运算符后直接按等于，重复上一次运算结果？根据PRD，应显示第一个操作数
        // 常见计算器此时将第一个操作数作为结果，不进行运算
        // 我们保持行为：显示第一个操作数，重置
        state.currentInput = formatOperand(state.previousOperand);
        state.expression = '';
        state.previousOperand = null;
        state.operator = null;
        state.waitingForOperand = false;
        state.justEvaluated = true;
        updateDisplay();
        return;
    }
    if (!state.operator || state.previousOperand === null || state.waitingForOperand) {
        // 没有运算符或只输入了一个数字，显示当前数字
        state.justEvaluated = true;
        updateDisplay();
        return;
    }
    // 正常执行计算
    // 保存当前输入作为第二个操作数（但performCalculation会读取state.currentInput）
    // 注意：performCalculation内部会构造表达式，所以我们提前保存用于第二个操作数的显示
    const prevInput = state.currentInput;
    const prevOperator = state.operator;
    const prevPrev = state.previousOperand;
    performCalculation();
    if (state.error) {
        // 如果出错，表达式已经在performCalculation中设置好（除零错误）
        // 但如果是其他错误，需要保留表达式
        if (!state.expression) {
            state.expression = formatOperand(prevPrev) + ' ' + getOperatorSymbol(prevOperator) + ' ' + prevInput + ' =';
            updateDisplay();
        }
        return;
    }
    // 正常：performCalculation 已经更新了state.expression
    // 无需额外操作
}

// ===== 退格 =====
function handleBackspace() {
    if (state.error) {
        // 错误状态下按退格等同于按C
        resetState();
        return;
    }
    if (state.justEvaluated) {
        // 刚显示结果，按退格等同于按C
        resetState();
        return;
    }
    if (state.waitingForOperand) {
        // 等待第二个操作数时按退格，删除当前输入（尚未输入或已输入部分）
        // 如果当前输入是'0'，则无变化；否则删除最后一位
        if (state.currentInput.length > 1) {
            state.currentInput = state.currentInput.slice(0, -1);
            if (state.currentInput === '' || state.currentInput === '-') {
                state.currentInput = '0';
            }
        } else {
            state.currentInput = '0';
        }
        updateDisplay();
        return;
    }
    // 正常输入模式下退格
    if (state.currentInput.length > 1) {
        state.currentInput = state.currentInput.slice(0, -1);
        if (state.currentInput === '' || state.currentInput === '-') {
            state.currentInput = '0';
        }
    } else {
        state.currentInput = '0';
    }
    updateDisplay();
}

// ===== 事件绑定 =====
const calculator = document.querySelector('.calculator');

calculator.addEventListener('click', (e) => {
    const btn = e.target.closest('button');
    if (!btn) return;
    const action = btn.dataset.action;
    const value = btn.dataset.value;

    switch (action) {
        case 'number':
            inputDigit(value);
            break;
        case 'decimal':
            inputDecimal();
            break;
        case 'operator':
            handleOperator(value);
            break;
        case 'equals':
            handleEquals();
            break;
        case 'clear':
            resetState();
            break;
        case 'backspace':
            handleBackspace();
            break;
    }
});

// ===== 键盘支持 =====
document.addEventListener('keydown', (e) => {
    const key = e.key;
    e.preventDefault(); // 防止页面滚动等默认行为

    if (key >= '0' && key <= '9') {
        inputDigit(key);
    } else if (key === '.') {
        inputDecimal();
    } else if (key === '+' || key === '-') {
        handleOperator(key);
    } else if (key === '*') {
        handleOperator('*');
    } else if (key === '/') {
        e.preventDefault(); // 阻止搜索等
        handleOperator('/');
    } else if (key === 'Enter' || key === '=') {
        e.preventDefault();
        handleEquals();
    } else if (key === 'Backspace') {
        e.preventDefault();
        handleBackspace();
    } else if (key === 'Escape' || key === 'c' || key === 'C') {
        e.preventDefault();
        resetState();
    }
});

// ===== 初始显示 =====
updateDisplay();